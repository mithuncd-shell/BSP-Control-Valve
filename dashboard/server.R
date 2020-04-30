options(shiny.port = 9999)
library(reticulate)
use_python("C:/ProgramData/Anaconda3/python.exe")
#total_valves = 13
import_from_path("handlers","C:/PAM/bsp_control_valve/Code/src")
PythonFile = "C:/PAM/bsp_control_valve/Code/src/handlers/collate_valve_status.py"
model_pat = "C:/PAM/bsp_control_valve/Code/data/live/models"
source_python(PythonFile)

EvaluateKPI<-function(){
  # Purpose    : Calculates on top of KPIStatus to calculates Signal for Dashboard
  # Input      :
  # Output     : KPI Signal Vector relevent 
  print(model_path)
  KPIDF <- collate_status(model_pat)
  # print(nrow(KPIDF[KPIDF$alarm==0,]))
  return(KPIDF)
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
update_plots <- function(model, top_act, output){
  if (model != "")
  {
    WFMObj<- load_valve_data(model_pat, paste(model))
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
library(shiny)
library(shinydashboard)
shinyServer(function(input,output, session)
{
  
  KPIDF<-EvaluateKPI()
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
})