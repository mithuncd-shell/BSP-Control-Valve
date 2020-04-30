library(reticulate)
library(shiny)
library(DT)

text11 = paste("\n   Plot Loading.\n",
             "       Please Wait for some Time\n",
             "       One might imagine useful informaiton here")

text_nodata = paste("\n   Select Different Filter.\n",
               "       No Data Points\n")

url_rmse <- a("RMSE", href="https://en.wikipedia.org/wiki/Root-mean-square_deviation")
url_mae <- a("MAE", href="https://en.wikipedia.org/wiki/Mean_absolute_error")
url_r2 <- a("R2", href="https://en.wikipedia.org/wiki/Coefficient_of_determination")
url_res <- a("Residual Plots Interpretation", href="http://docs.statwing.com/interpreting-residual-plots-to-improve-your-regression/#x-unbalanced-header")

use_python("C:/ProgramData/Anaconda3/python.exe")
main_script = "C:/PAM/bsp_control_valve/Code/src/valvesPAM.py"
use_pyth = "C:\\ProgramData\\Anaconda3\\python.exe"
wd = "C:\\PAM\\bsp_control_valve\\Code\\"
import_from_path("handlers","C:/PAM/bsp_control_valve/Code/src")
PythonFile = "C:/PAM/bsp_control_valve/Code/src/handlers/collate_valve_status_new.py"
model_pat = "C:/PAM/bsp_control_valve/Code/data/live/models"

source_python(PythonFile)

EvaluateKPI<-function(){
  # Purpose    : Calculates on top of KPIStatus to calculates Signal for Dashboard
  # Input      :
  # Output     : KPI Signal Vector relevent 
  #print(model_pat)
  KPIDF <- collate_status(model_pat)
  # print(nrow(KPIDF[KPIDF$alarm==0,]))
  return(KPIDF)
}


Trainingpkl<-function(){
  # Purpose    : Get pkl file in training folder
  # Input      :
  # Output     : list of pkl files in training folder 
  #print(model_pat)
  PKLDF <- get_pickle(model_path)
  # print(nrow(KPIDF[KPIDF$alarm==0,]))
  return(PKLDF)
}

GetPredictStoreValves<-function(KPIDF){
  # Purpose    : Gets the valveNames from PredictStore.csv
  # Input      :
  # Output     : List of Valves Online
  return(KPIDF$valve_id)
}

GetTopFeatures <- function(DF,N){
  # Purpose    : To Get top N correlated Features
  # Input      :
  # Output     :
  #Get Top N Values
  FList <- colnames(DF)
  SList<-FList[(1:N)]
  return(SList)
}

TransformObjToDF <- function(MDF,N){

  NewDF<-data.frame(DateTime=as.POSIXct(strptime(MDF$datetime, format="%Y-%m-%d %H:%M:%S")))
  NewDF$actual<-MDF$target
  NewDF$prediction<- as.vector(MDF$prediction)
  NewDF$alarm<- as.vector(MDF$alarm)
  NewDF$alarm_trigger<- as.vector(MDF$alarm_trigger)
  NewDF$deviation<- as.vector(MDF$deviation)
  NewDF$mode<- as.vector(MDF$filter)
  if (N>0)
  {
    ExtraTags<-GetTopFeatures(MDF,N)
    EDF<-subset(MDF,select = ExtraTags)
    NewDF<-cbind(NewDF,EDF)
  }
  NoNA_TSDF<-NewDF[!(is.na(NewDF$DateTime)),]
  #TSDF<-as.ts(x = NewDF)
  return(NoNA_TSDF)
}

TransformObjToDF1 <- function(MDF,s,e){
  NewDF<-data.frame(DateTime=as.POSIXct(strptime(MDF$datetime, format="%Y-%m-%d %H:%M:%S")))
  NewDF$actual<-MDF$target
  NewDF$prediction<- as.vector(MDF$prediction)
  NewDF$deviation<- as.vector(MDF$deviation)
  
  s = as.POSIXct(strptime(paste(s,"00:00:00"), format="%Y-%m-%d %H:%M:%S"))
  e = as.POSIXct(strptime(paste(e,"00:00:00"), format="%Y-%m-%d %H:%M:%S"))
  NewDF = data.frame( NewDF[(NewDF$DateTime > s) & (NewDF$DateTime < e),] )
  return(NewDF)
}

TransformObjToDF2 <- function(MDF,s,e){
  s = as.POSIXct(strptime(paste(s,"00:00:00"), format="%Y-%m-%d %H:%M:%S"))
  e = as.POSIXct(strptime(paste(e,"00:00:00"), format="%Y-%m-%d %H:%M:%S"))
  rownames(MDF) = as.POSIXct(strptime(paste(rownames(MDF),"00:00:00"), format="%Y-%m-%d %H:%M:%S"))
  NewDF = MDF[(rownames(MDF) > s) & (rownames(MDF) < e),]
  return(NewDF)
}

update_plots <- function(model, top_act, output){
  if (model != "")
  {
    WFMObj<- load_valve_data180(model_pat, paste(model))
    #Draw Default Valve Details
    # Retrive Data from the WFM File
    TTS<-TransformObjToDF(WFMObj,top_act)
    TagsToPlot<-c("actual","prediction")
    if (top_act>0)
    {
      # print("top actors", top_act)
      ExtraTags<-GetTopFeatures(WFMObj,top_act)
      TagsToPlot<-append(TagsToPlot,ExtraTags)
    }
    
    data=xts(x = TTS[,TagsToPlot],order.by =TTS$DateTime)
    
    #Draw primary Graph (Predicted & Actual -> timeseries)
    output$actual_vs_predict_gph <- renderDygraph(
      {dygraph(data, main = "Prediction", group = "Evaluate") %>% dyAxis("y", label = "Actual vs Predicted", valueRange = c(-10,110) )}
    ) 
    #Draw Second Graph (Actual differene -> timeseries)
    data2=xts(x = TTS[,c("deviation")],order.by =TTS$DateTime)
    colnames(data2) <- c("Deviation")
    output$deviation_gph <- renderDygraph(
      {dygraph(data2, main = "Deviation", group = "Evaluate") %>% dyAxis("y", label = "Deviation", valueRange = c(-20,20) )}
    )
    #Draw third Graph (Alarm -> timeseries)
    data3=xts(x = TTS[,c("alarm","alarm_trigger")],order.by =TTS$DateTime)
    colnames(data3)<-c("Alarm","Email_Trigger")
    output$alarm_gph <- renderDygraph(
      {dygraph(data3, main = "Alarm", group = "Evaluate")%>% dyAxis("y", label = "Alarm & Email Alert")}
    )
    #Draw fourth Graph (mode -> timeseries)
    data4=xts(x = TTS[,c("mode")],order.by =TTS$DateTime)
    colnames(data4)<-c("Mode")
    output$mode_gph <- renderDygraph(
      {dygraph(data4, main = "Mode", group = "Evaluate")%>% dyAxis("y", label = "Mode(Auto(0)/Manual(1)") %>% dyRangeSelector()}
    )
    RanOnce=TRUE
  }
  
}

update_residualplots_tr <- function(model, d, output){
  if(model != "")
  {
    WFMObj<- load_valve_data(model_path, paste(model))
    if(d[1] < d[2]){
    TTS<-TransformObjToDF1(WFMObj,d[1],d[2])
    TTS = TTS[,c('actual','prediction','deviation')]
    output$ResidualPlot_tr <- renderPlot(
      ggplot(TTS, aes(x = actual, y = deviation)) + geom_point() 
      + theme(panel.background = element_rect(fill = 'white'), panel.grid.major = element_line(colour = "black"), panel.border = element_rect(linetype = "solid", fill = NA),
              axis.text=element_text(size=15),axis.title=element_text(size=15,face="bold"),plot.title = element_text(size=20,hjust = 0.5)) 
      +  xlab("Actual Valve Opening") + ylab("Difference b/w Actual and Predicted Valve Opening") + ggtitle("Residual Plot"))
    }else(
      output$ResidualPlot_tr <- renderPlot(
        ggplot() + 
          annotate("text", x = 4, y = 25, size=8, label = text_nodata) + 
          theme_bw() +
          theme(panel.grid.major=element_blank(),
                panel.grid.minor=element_blank())
      )
    )
  }else(
  output$ResidualPlot_tr <- renderPlot(
    ggplot() + 
      ggplot2::annotate("text", x = 4, y = 25, size=8, label = text11) + 
      theme_bw() +
      theme(panel.grid.major=element_blank(),
            panel.grid.minor=element_blank())
    )
  )
}

update_residualplots_te <- function(model, d, output){
  if(model != "")
  {
    WFMObj<- load_valve_data(model_path, paste(model))
    if(d[1] < d[2]){
    TTS<-TransformObjToDF1(WFMObj,d[1],d[2])
    TTS = TTS[,c('actual','prediction','deviation')]
    
    output$ResidualPlot_te <- renderPlot(
      ggplot(TTS, aes(x = actual, y = deviation)) + geom_point() 
      + theme(panel.background = element_rect(fill = 'white'), panel.grid.major = element_line(colour = "black"), panel.border = element_rect(linetype = "solid", fill = NA),
              axis.text=element_text(size=15),axis.title=element_text(size=15,face="bold"),plot.title = element_text(size=20,hjust = 0.5)) 
      +  xlab("Actual Valve Opening") + ylab("Difference b/w Actual and Predicted Valve Opening") + ggtitle("Residual Plot"))
    }else(
      output$ResidualPlot_te <- renderPlot(
        ggplot() + 
          annotate("text", x = 4, y = 25, size=8, label = text_nodata) + 
          theme_bw() +
          theme(panel.grid.major=element_blank(),
                panel.grid.minor=element_blank())
      )
      
    )
    }else(
      output$ResidualPlot_te <- renderPlot(
        ggplot() + 
          ggplot2::annotate("text", x = 4, y = 25, size=8, label = text11) + 
          theme_bw() +
          theme(panel.grid.major=element_blank(),
                panel.grid.minor=element_blank())
      )
        
    )
}

hist_tr <- function(model, e, d, output){

  if(model != "")
  {
    WFMObj<- load_valve_data(model_path, paste(model))
    
    if(d[1] < d[2]){
    TTS<-TransformObjToDF1(WFMObj,d[1],d[2])
    DF <- rbind(data.frame(fill="green", obs=TTS$actual), data.frame(fill="blue", obs=TTS$prediction))

    output$histplot_tr <- renderPlot(
      ggplot(aes(x = obs, fill=fill), data = DF)+ aes(y=stat(count)/sum(stat(count))) 
      + geom_histogram(breaks=c(seq(0, 100, by=as.integer(e))),binwidth=10, color='black', position = "dodge")+ scale_fill_manual(name="Group",values=c("green","blue"),labels=c("Actual","Prediction"))
      + theme(panel.background = element_rect(fill = 'white'), panel.grid.major = element_line(colour = "black"), panel.border = element_rect(linetype = "solid", fill = NA),
              axis.text=element_text(size=15),axis.title=element_text(size=15,face="bold"),plot.title = element_text(size=20,hjust = 0.5))
      +  xlab("Valve Opening")+ ylab("Fraction of Opening") + ggtitle("Histogram Plot"))
    }else( output$histplot_tr <- renderPlot(
      ggplot() + 
        annotate("text", x = 4, y = 25, size=8, label = text_nodata) + 
        theme_bw() +
        theme(panel.grid.major=element_blank(),
              panel.grid.minor=element_blank())
        ) 
      )
  }else(    output$histplot_tr <- renderPlot(
      ggplot() + 
        annotate("text", x = 4, y = 25, size=8, label = text11) + 
        theme_bw() +
        theme(panel.grid.major=element_blank(),
              panel.grid.minor=element_blank())
                ) 
              )
}

hist_te <- function(model, e, d, output){
  if(model != "")
  {
    WFMObj<- load_valve_data(model_path, paste(model))
    if(d[1] < d[2]){
    TTS<-TransformObjToDF1(WFMObj,d[1],d[2])
    DF <- rbind(data.frame(fill="green", obs=TTS$actual), data.frame(fill="blue", obs=TTS$prediction))
    
    output$histplot_te <- renderPlot(
      ggplot(aes(x = obs, fill=fill), data = DF)+ aes(y=stat(count)/sum(stat(count))) 
      + geom_histogram(breaks=c(seq(0, 100, by=as.integer(e))),binwidth=10, color='black', position = "dodge")+ scale_fill_manual(name="Group",values=c("green","blue"),labels=c("Actual","Prediction"))
      + theme(panel.background = element_rect(fill = 'white'), panel.grid.major = element_line(colour = "black"), panel.border = element_rect(linetype = "solid", fill = NA),
              axis.text=element_text(size=15),axis.title=element_text(size=15,face="bold"),plot.title = element_text(size=20,hjust = 0.5))
      +  xlab("Valve Opening")+ ylab("Fraction of Opening") + ggtitle("Histogram Plot")) 
    }else(
      output$histplot_te <- renderPlot(
        ggplot() + 
          annotate("text", x = 4, y = 25, size=8, label = text_nodata) + 
          theme_bw() +
          theme(panel.grid.major=element_blank(),
                panel.grid.minor=element_blank())
      ) 
    )
    }else(
      output$histplot_te <- renderPlot(
        ggplot() + 
          annotate("text", x = 4, y = 25, size=8, label = text11) + 
          theme_bw() +
          theme(panel.grid.major=element_blank(),
                panel.grid.minor=element_blank())
        ) 
    )
}

kpi_return_tr <- function(model, d, output){
  if ((model != "") & (d[1] < d[2]))
  {kpi<- training_data_kpi(model_path, paste(model), start_date =d[1] , end_date = d[2])
    output$tr_MSE = renderValueBox({valueBox(paste0("RMSE: ", round(as.numeric(kpi[1]),1)), subtitle = "", icon = icon("chart-line"), color = "blue")   })  
    output$tr_MAE = renderValueBox({valueBox(paste0("MAE: " , round(as.numeric(kpi[2]),1)), subtitle = "", icon = icon("chart-line"), color = "blue")   })  
    output$tr_R2  = renderValueBox({valueBox(paste0("R2: "  , round(as.numeric(kpi[3]),2)), subtitle = "", icon = icon("chart-line"), color = "blue")   })  
  }else{
    output$tr_MSE = renderValueBox({valueBox(paste0("RMSE: ", "NA"), subtitle = "", icon = icon("chart-line"), color = "blue")   })  
    output$tr_MAE = renderValueBox({valueBox(paste0("MAE: " , "NA"), subtitle = "", icon = icon("chart-line"), color = "blue")   })  
    output$tr_R2  = renderValueBox({valueBox(paste0("R2: "  , "NA"), subtitle = "", icon = icon("chart-line"), color = "blue")   })  
  }
}

kpi_return_te <- function(model, d, output){
  if ((model != "") & (d[1] < d[2]))
  {
    kpi<- testing_data_kpi(model_path, paste(model), start_date = d[1], end_date = d[2])
    output$te_MSE = renderValueBox({valueBox(paste0("RMSE: ",round(as.numeric(kpi[1]),1)), subtitle = "" ,icon = icon("chart-line"),color = "blue") })  
    output$te_MAE = renderValueBox({valueBox(paste0("MAE: ",round(as.numeric(kpi[2]),1)), subtitle = ""  ,icon = icon("chart-line"),color = "blue") })  
    output$te_R2  = renderValueBox({valueBox(paste0("R2: ",round(as.numeric(kpi[3]),2)), subtitle = ""   ,icon = icon("chart-line"),color = "blue") })  
  }else{
    output$te_MSE = renderValueBox({valueBox(paste0("RMSE: ","NA"), subtitle = "" ,icon = icon("chart-line"),color = "blue") })  
    output$te_MAE = renderValueBox({valueBox(paste0("MAE: ","NA"), subtitle = ""  ,icon = icon("chart-line"),color = "blue") })  
    output$te_R2  = renderValueBox({valueBox(paste0("R2: ","NA"), subtitle = ""   ,icon = icon("chart-line"),color = "blue") }) 
  }
}

df_co <- function(model, output){
  if( model != ""){
  x = get_coeff1(model_path,model)
   
  output$table = shiny::renderDataTable({
     t = get_coeff1(model_path,model)
     colnames(t)[1] = "PI Tags"
     t
  },options= list(pageLength=5))
  }else(
    output$table = shiny::renderDataTable({
      iris
    })
  )
}

df_eq <- function(model, output){
  if(model != ""){
  df = get_coeff1(model_path,model)
  
  t = mapply(function(a,b){paste0("(","(",a,")","*",b,")")}, df$Coefficient, df$Input_column)
  ee = paste(t, collapse = " + ")
  ee = paste("Y(Predicted Valve opening) = ",ee)
  output$equation =  renderText({ (ee) })
  }else(  output$equation =  renderText({ ("Loading!!")})
          )
}

df_list_config <- function(){
  df = list.files(model_path,full.names = F,pattern='pkl')
  df = gsub(".pkl","",df[-grep("status",df)])
  return(df)
}

df_valveinfo <- function(m,output){
  confnames = config_names()
  confnames = gsub(".json","",confnames)
  text = "Uploading"
  if(m %in% confnames){
    path = paste0(config_path,"\\",m,".json")
    mod_time = as.character(file.info(path)$mtime)
    text = paste("Available", "- Last Modified DateTime", mod_time)
  }else{text = "New Valve"}
  
  output$valve_info = renderText({text}) 
}

mcolumn <- function(){
  df = master_column()
  nam = sprintf("column[%s]",seq(1:length(df)))
  names(df) <- nam
  return(df)
}

mselect <- function(input){
  va = input$new_valve
  if(va != ""){
    KPIDF<-EvaluateKPI()
    valves = KPIDF$valve_id
    if(va %in% valves){
      data = read_json(va)
      e = data['exclusion_pi_tags'][[1]]
    }else{e = ""}
  }else{e = ""}
  return(e)
}
mselect1 <- function(input){
  va = input$new_valve
  if(va != ""){
    KPIDF<-EvaluateKPI()
    valves = KPIDF$valve_id
    if(va %in% valves){
      data = read_json(va)
      e = data['inclusion_pi_tags'][[1]]
    }else{e = ""}
  }else{e = ""}
  return(e)
}
df_default_config <- function(input){
  va = input$new_valve
  if(va != ""){
    KPIDF<-EvaluateKPI()
    valves = KPIDF$valve_id
    if(va %in% valves){
      data = read_json(va)
      type = data['type'][[1]]
      location = data['location'][[1]]
      valveplant = data['ValvePlant'][[1]]
      oppitag = data['op_pi_tag'][[1]]
      description = data['description'][[1]]
      
      trstart = data['training_period'][[1]][[1]]
      trend = data['training_period'][[1]][[2]]
      testart = data['testing_period'][[1]][[1]]
      teend = data['testing_period'][[1]][[2]]
      
      algo = data['model'][[1]]
      maxfeature = data['maximum_features'][[1]]
      modepitag = data['mode_pi_tag'][[1]]
      filtercond = data['filter_conditions'][[1]]
      filterpitag = data['filter_pi_tags'][[1]]
      
      exclusiontag = data['exclusion_pi_tags'][[1]]
      bplower = data['band_pass_lower_limit'][[1]]
      bpupper = data['band_pass_upper_limit'][[1]]
      deviation_thres = data['deviation_threshold'][[1]]
      alarm_trig = data['alarm_trigger'][[1]]
      alarm_stop = data['alarm_stop'][[1]]
      interval =  as.numeric(gsub("[^0-9.-]+", "", data['interval'][[1]])) 
      piservername = data['PIServerName'][[1]]
      inclusiontag = data['inclusion_pi_tags'][[1]]

    }else{type = "FCV"
    location = "location"
    valveplant = "BSP Champion 7"
    oppitag = "op_pi_tag"
    description = "description"
    trstart = "2017-09-10" #Year-Month-Date
    trend = "2018-09-10"
    testart = "2018-09-10"
    teend = "2019-06-10"
    algo = 'Ridge'
    maxfeature = 50
    filtercond = 'filter_conditions'
    filterpitag = 'filter_pi_tags'
    modepitag = 'mode_pi_tag'
    exclusiontag = list("CPCB07-DCS-PICA740SP", "CPCB07-DCS-LICA742HL")
    bplower = 0.05
    bpupper = 99.95
    deviation_thres = 5
    alarm_trig = 30
    alarm_stop = 48
    interval = 10
    piservername = ''
    inclusiontag = list()
    }
  }else{type = "FCV"
  location = "location"
  valveplant = "BSP Champion 7"
  oppitag = 'op_pi_tag'
  description = 'description'
  trstart = "trstart"
  trend = 'training_period'
  testart = 'testing_period'
  teend = 'testing_period'
  algo = 'model'
  maxfeature = 'maximum_features'
  filtercond = 'filter_conditions'
  filterpitag = 'filter_pi_tags'
  modepitag = 'mode_pi_tag'
  exclusiontag = 'exclusion_pi_tags'
  bplower = 'band_pass_lower_limit'
  bpupper = 'band_pass_upper_limit'
  deviation_thres = 'deviation_threshold'
  alarm_trig = 'alarm_trigger'
  alarm_stop = 'alarm_stop'
  interval = 'interval'
  piservername = ''
  inclusiontag = list()
  }
  
  result = list(type, location, valveplant, oppitag, description, trstart, trend, testart, teend, algo, maxfeature, modepitag, filtercond, filterpitag, 
                exclusiontag, bplower, bpupper, deviation_thres, alarm_trig, alarm_stop, piservername, interval ,inclusiontag )
  
  return(result)
}

#new for download
df_update_bat <- function(b){
  cmdcom=paste0(use_pyth,' "',main_script,'" ',"train ",b$new_valve,' >"',wd,'\\train-results.log"')
  p = paste0(wd,"\\","train-valves.bat")
  write(cmdcom,p)
  cmdcom=paste0(use_pyth,' "',main_script,'" ',"deploy ",b$new_valve,' >"',wd,'\\deploy-results.log"')
  p = paste0(wd,"\\","deploy-valves.bat")
  write(cmdcom,p)
  
}
df_create_config <- function(a){
  config_new = list()
  
    config_new[["valve_id"]] = a$new_valve
    config_new[["location"]] = a$Location_textinput
    config_new[["type"]] = a$type_textinput
    config_new[["description"]] = a$description_textinput
    config_new[['op_pi_tag']] = a$new_valve
    config_new[['mode_pi_tag']] = a$modepitag
    config_new[["filter_pi_tags"]] = a$filterpitag
    config_new[["filter_conditions"]] = list(a$filtercond)
    
    if(length(a$exclusiontag)==0){
      config_new[['exclusion_pi_tags']] = list("")
    }else if(length(a$exclusiontag)==1){
      config_new[['exclusion_pi_tags']] = list(a$exclusiontag)
    }else{
      config_new[['exclusion_pi_tags']] = a$exclusiontag
    }
    
    if(length(a$inclusiontag)==0){
      config_new[['inclusion_pi_tags']] = list("")
    }else if(length(a$inclusiontag)==1){
      config_new[['inclusion_pi_tags']] = list(a$inclusiontag)
    }else{
      config_new[['inclusion_pi_tags']] = a$inclusiontag
    }
    
    config_new[["maximum_features"]]  = as.numeric(a$maxfeature)
    config_new[['band_pass_lower_limit']] = as.numeric(a$bplower)
    config_new[['band_pass_upper_limit']] = as.numeric(a$bpupper)
    
    trs = as.POSIXct(strptime(paste(a$trstart_textinput,"00:00:00"), format="%Y-%m-%d %H:%M:%S"))
    tre = as.POSIXct(strptime(paste(a$trend_textinput,"23:50:00"), format="%Y-%m-%d %H:%M:%S"))
    tes = as.POSIXct(strptime(paste(a$testart_textinput,"00:00:00"), format="%Y-%m-%d %H:%M:%S"))
    tee = as.POSIXct(strptime(paste(a$teend_textinput,"23:50:00"), format="%Y-%m-%d %H:%M:%S"))

    config_new[["training_period"]] = list(as.character(trs), as.character(tre))
    config_new[["testing_period"]] =  list(as.character(tes), as.character(tee))
    config_new[["deviation_threshold"]] = as.numeric(a$deviation_thres)
    config_new[["alarm_trigger"]] = as.numeric(a$alarm_trig)
    config_new[['alarm_stop']] = as.numeric(a$alarm_stop)
    config_new[['interval']] = paste0(a$interval,"m")
    config_new[['PIServerName']] = a$piservername
    config_new[['pi_write_back_tag']] = list(a$pi_write_back_tag1, a$pi_write_back_tag2)
    config_new[['model']] = a$algo
    config_new[['ValvePlant']] = a$valveplant_textinput
          
    config_new = toJSON(config_new)
    p = paste0(config_path,"\\",a$new_valve,".json")
    write(config_new, p)
}

scatter_1 <- function(pv, fv, dm, ym, dr, output){
  if((pv != "") & (fv != ""))
  {
    WFMObj<- read_master_file()
    TTS<-TransformObjToDF2(WFMObj,dr[1],dr[2])
    
    if(nrow(TTS)>0){
    TTS <- TTS[,c(pv,fv)]
    
    if(pv == fv){
      TTS <- TTS[pv]
      con = is.finite(as.numeric(TTS[[pv]]))
      rn = rownames(TTS)[con]
      TTS = data.frame(TTS[ con, ])
      colnames(TTS) = pv
      if(dm == "Quarter"){
        Date_Metric = as.yearqtr(rn, format = "%Y-%m-%d")
      }else if(dm == "Month"){
        Date_Metric = format(as.Date(rn), "%Y-%m")
      }else if(dm == "Week"){
        Date_Metric = format(as.Date(rn), "%Y-%V")
      }else{ Date_Metric = "Wrong"}
      
      TTS = data.frame(lapply(TTS, function(x) { scales::rescale(x, to= c(0,100))}))
      colnames(TTS) = gsub("\\.", "-", colnames(TTS))
      TTS$Date_Metric = as.factor(Date_Metric)
    }else{
      TTS = TTS[ is.finite(as.numeric(TTS[[pv]])) & is.finite(as.numeric(TTS[[fv]])), ]
      if(dm == "Quarter"){
        Date_Metric = as.yearqtr(rownames(TTS), format = "%Y-%m-%d")
      }else if(dm == "Month"){
        Date_Metric = format(as.Date(rownames(TTS)), "%Y-%m")
      }else if(dm == "Week"){
        Date_Metric = format(as.Date(rownames(TTS)), "%Y-%V")
      }else{ Date_Metric = "Wrong"}
      
      TTS = data.frame(lapply(TTS, function(x) { scales::rescale(x, to= c(0,100))}))
      colnames(TTS) = gsub("\\.", "-", colnames(TTS))
      TTS$Date_Metric = "random"
      TTS$Date_Metric = as.factor(Date_Metric)
    }
    
    if(ym=="Log"){
      TTS[[pv]] = log10(TTS[[pv]])
    }
    
    output$scatter_process_flow <- renderPlot(
        ggplot(data = TTS, aes(x = TTS[[fv]], y = TTS[[pv]], color=Date_Metric)) + geom_point(size=2)
        + theme(panel.background = element_rect(fill = 'white'), panel.grid.major = element_line(colour = "black"), panel.border = element_rect(linetype = "solid", fill = NA),
                axis.text=element_text(size=15),axis.title=element_text(size=15,face="bold"),plot.title = element_text(size=20,hjust = 0.5))
        + ggtitle("Plot") + xlab(fv) + ylab(pv)
        )
    }else(
      output$scatter_process_flow <- renderPlot(
        ggplot() + 
          annotate("text", x = 4, y = 25, size=8, label = text_nodata) + 
          theme_bw() +
          theme(panel.grid.major=element_blank(),
                panel.grid.minor=element_blank())
      )
    )
  }else(
    output$scatter_process_flow <- renderPlot(
      ggplot() + 
        annotate("text", x = 4, y = 25, size=8, label = text11) + 
        theme_bw() +
        theme(panel.grid.major=element_blank(),
              panel.grid.minor=element_blank())
      )
  )
}

process_timeseries <- function(pv, fv, dr, output){
  if((pv != "") & (fv != ""))
  {
    WFMObj <- read_master_file()
    TTS <- TransformObjToDF2(WFMObj,dr[1],dr[2])
    
    if(nrow(TTS)>0){
    TTS <- TTS[,c(pv,fv)]
    
    KPIDF<-EvaluateKPI()
    valves = KPIDF$valve_id
    if(fv %in% valves){
      WFMObj <- load_valve_data(model_path, paste(fv))
      TTS2 <- TransformObjToDF1(WFMObj,dr[1],dr[2])
      TTS2 = TTS2[,c('actual','prediction')]
      TTS = cbind(TTS, TTS2)
      TTS = TTS[ , !names(TTS) %in% c("actual")]
    }
    rn = as.POSIXct(strptime(paste(rownames(TTS),"00:00:00"), format="%Y-%m-%d %H:%M:%S"))
    # TTS_copy = TTS
    # colnames(TTS_copy) = paste0(colnames(TTS),"_org")
    # TTS = data.frame(lapply(TTS, function(x) { scales::rescale(x, to= c(0,100))}))
    # TTS = cbind(TTS,TTS_copy)
    
    TTS_2 = TTS
    TTS = xts(x = TTS,order.by = rn)
    
    # output$box_month <- renderPlot({
    #   boxplot(TTS_2[[pv]] ~ reorder(format(as.Date(rownames(TTS_2)),'%b %y'),as.Date(rownames(TTS_2))), outline = FALSE)
    # })

    output$box_month <- renderPlot({
    ggplot(TTS_2) +
      geom_boxplot(aes(y=TTS_2[[pv]],
                       x=reorder(format(as.Date(rownames(TTS_2)),'%b %Y'),as.Date(rownames(TTS_2))),
                       fill=format(as.Date(rownames(TTS_2)),'%Y'))) +
      xlab('Month') + guides(fill=guide_legend(title="Year")) +
      theme_bw()
    })
    
    output$process_timeseries <- renderDygraph(
      {dygraph(TTS, main = "Time Series") %>% dyAxis("y", label = "Valve Opening and Process Output", valueRange = c(-10,110) )}
    )
    }else(
      output$process_timeseries <- renderDygraph(
        ggplot() + annotate("text", x = 4, y = 25, size=8, label = text_nodata) + 
          theme_bw() + theme(panel.grid.major=element_blank(), panel.grid.minor=element_blank())
      )
    )
    }else(
    output$process_timeseries <- renderDygraph(
      ggplot() + annotate("text", x = 4, y = 25, size=8, label = text11) + 
        theme_bw() + theme(panel.grid.major=element_blank(), panel.grid.minor=element_blank())
      )
    )
}

library(shiny)
library(shinydashboard)
shinyServer(function(input,output, session)
{
   
  KPIDF<-EvaluateKPI()
  PKLDF<-Trainingpkl()
  print(PKLDF)
  # WFMObj<- load_valve_data(paste("26FCV1161"))
  output$Green <- renderValueBox(
      {
        valueBox(nrow(KPIDF[KPIDF$alarm==0,]),"Valves Performing Good",icon = icon("check-circle"),color = "green")
      }
    )
  output$Yellow <- renderValueBox(
      {
        valueBox("Last Update:",paste(max(KPIDF$last_predicted_time_stamp)),icon = icon("clock"),color = "blue")
      }
    )
  
  output$Red <- renderValueBox(
      {
        valueBox(nrow(KPIDF[KPIDF$alarm==1,]),"Values not Performing as expected",icon = icon("times-circle"),color = "red")
      }
    )
  lapply(1:total_boxes, 
           function(i)
             {
             output[[paste0('IFBox', i)]] <- renderInfoBox(
               {
               infoBox(paste(KPIDF[i,]$PI.Tag),
                       actionLink(inputId = paste("Evaluate",KPIDF[i,]$valve_id,sep="_"), label = paste(KPIDF[i,]$valve_id)), 
                       a(paste(KPIDF[i,]$description)),
                       icon = icon(paste(KPIDF[i,]$icon)),
                       color = paste(KPIDF[i,]$color))
               })
             }
    )
  
  # output$ex1 <- renderUI({
  #   withMathJax(helpText('Dynamic output 1:  $$\\alpha^2$$'))
  # })
   
  updateSelectInput(session,"ModelSelector", choices = KPIDF$valve_id, selected = paste(KPIDF[1,]$valve_id))
  ALLEvents<- lapply(
      1:total_boxes, function (i)
      {
        observeEvent(input[[paste("Evaluate",KPIDF[i,]$valve_id,sep="_")]], 
        {
          updateTabItems(session, "tabs",selected = "six")
          updateSelectInput(session, "ModelSelector", selected = paste(KPIDF[i,]$valve_id))
        }
        )
        # print("selected", input$ModelSelector)
      }
    )
   
  updateSelectInput(session, "ModelSelector", selected = KPIDF[1,]$valve_id)
  RanOnce=FALSE
   
  observeEvent(input$ModelSelector,{update_plots(input$ModelSelector,input$TopActors, output)})
  observeEvent(input$TopActors,{update_plots(input$ModelSelector,input$TopActors, output)})
  
  updateSelectInput(session,"ModelSelector1", choices = PKLDF$valve_id, selected = paste(KPIDF[1,]$valve_id))
  
  observeEvent(c(input$ModelSelector1, input$daterange_tr), {update_residualplots_tr(input$ModelSelector1, input$daterange_tr, output)})  
  
  observeEvent(c(input$ModelSelector1, input$daterange_te), {update_residualplots_te(input$ModelSelector1, input$daterange_te, output)})  

  observeEvent(c(input$ModelSelector1, input$daterange_tr, input$bins_tr), {hist_tr(input$ModelSelector1, input$bins_tr, input$daterange_tr, output)})  
  
  observeEvent(c(input$ModelSelector1, input$daterange_te, input$bins_tr), {hist_te(input$ModelSelector1, input$bins_tr, input$daterange_te, output)})  
  
  observeEvent(c(input$ModelSelector1, input$daterange_tr), {kpi_return_tr(input$ModelSelector1, input$daterange_tr, output)}) 
  
  observeEvent(c(input$ModelSelector1, input$daterange_te), {kpi_return_te(input$ModelSelector1, input$daterange_te, output)})

  observeEvent(c(input$ModelSelector1), {df_co(input$ModelSelector1, output)})
  
  observeEvent(c(input$ModelSelector1), {df_eq(input$ModelSelector1, output)})
  
  observe({updateSelectInput(session, "new_valve",choices = mcolumn() )})
  observe({updateSelectInput(session, "modepitag",choices = mcolumn() )})
  observe({updateSelectInput(session, "exclusiontag",choices = mcolumn() )})
  observe({updateSelectInput(session, "inclusiontag",choices = mcolumn() )})
  observe({updateSelectInput(session, "process_valve",choices = mcolumn() )})
  observe({updateSelectInput(session, "flow_valve",choices = mcolumn() )})
  
  observeEvent(c(input$new_valve), {df_valveinfo(input$new_valve, output)})
  
  observe({updateTextInput(session, "type_textinput", value = df_default_config(input)[[1]][1] )})
  observe({updateTextInput(session, "Location_textinput", value = df_default_config(input)[[2]][1] )})
  observe({updateTextInput(session, "valveplant_textinput", value = df_default_config(input)[[3]][1] )})
  observe({updateTextInput(session, "oppitag_textinput", value = df_default_config(input)[[4]][1] )})
  observe({updateTextInput(session, "description_textinput", value = df_default_config(input)[[5]][1] )})
  observe({updateTextInput(session, "trstart_textinput", value = df_default_config(input)[[6]][1] )})
  observe({updateTextInput(session, "trend_textinput", value = df_default_config(input)[[7]][1] )})
  observe({updateTextInput(session, "testart_textinput", value = df_default_config(input)[[8]][1] )})
  observe({updateTextInput(session, "teend_textinput", value = df_default_config(input)[[9]][1] )})
  observe({updateTextInput(session, "algo", value = df_default_config(input)[[10]][1] )})
  observe({updateTextInput(session, "maxfeature", value = df_default_config(input)[[11]][1] )})
  observe({updateTextInput(session, "modepitag", value = df_default_config(input)[[12]][1] )})
  observe({updateTextInput(session, "filtercond", value = df_default_config(input)[[13]][1] )})
  observe({updateTextInput(session, "filterpitag", value = df_default_config(input)[[14]][1] )})
  observe({updateTextInput(session, "exclusiontag", value = df_default_config(input)[[15]][1] )})
  observe({updateTextInput(session, "bplower", value = df_default_config(input)[[16]][1] )})
  observe({updateTextInput(session, "bpupper", value = df_default_config(input)[[17]][1] )})
  observe({updateTextInput(session, "deviation_thres", value = df_default_config(input)[[18]][1] )})
  observe({updateTextInput(session, "alarm_trig", value = df_default_config(input)[[19]][1] )})
  observe({updateTextInput(session, "alarm_stop", value = df_default_config(input)[[20]][1] )})
  observe({updateTextInput(session, "piservername", value = df_default_config(input)[[21]][1] )})
  observe({updateTextInput(session, "interval", value = df_default_config(input)[[22]][1] )})
  observe({updateTextInput(session, "inclusiontag", value = df_default_config(input)[[23]][1] )})
  observe({updateSelectInput(session, "exclusiontag",selected = mselect(input) )})
  observe({updateSelectInput(session, "inclusiontag",selected = mselect1(input) )})
  observeEvent(input$create, {df_create_config(input)})
  
  observeEvent(input$updatebat, {df_update_bat(input)})
  observeEvent(c(input$process_valve, input$flow_valve, input$color, input$log_normal, input$dr_flow),
               {scatter_1(input$process_valve, input$flow_valve, input$color, input$log_normal, input$dr_flow, output)})
  
  observeEvent(c(input$process_valve, input$flow_valve, input$dr_flow),
               {process_timeseries(input$process_valve, input$flow_valve, input$dr_flow, output)})

  observeEvent(input$retrain, {  shell.exec(paste0(wd,"train-valves.bat"))    })
  observeEvent(input$deploy,  {  shell.exec(paste0(wd,"deploy-valves.bat"))    })
  #observeEvent(input$delete,  {  shell.exec(paste0(wd,"update-valves.bat"))    })
  #new for download
  
  fileName <- "train-results.log"
  
  output$traininglog <- downloadHandler(
    filename = function() {
      fileName 
    },
    content = function(file) {
      file.copy(file.path(wd, fileName), file)
    }
  )
  
  fileNamedep <- "deploy-results.log"
  
  output$deploymentlog <- downloadHandler(
    filename = function() {
      fileNamedep
    },
    content = function(file) {
      file.copy(file.path(wd, fileNamedep), file)
    }
  )
  #new end  
  
  output$url_rmse <- renderUI({
    tagList("Link :", url_rmse)
  })
  output$url_mae <- renderUI({
    tagList("Link:", url_mae)
  })
  output$url_r2 <- renderUI({
    tagList("Link:", url_r2)
  })
  output$url_res <- renderUI({
    tagList("Link:", url_res)
  })
})



