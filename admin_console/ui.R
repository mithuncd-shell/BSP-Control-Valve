################ Packages Required ###########
library(shiny)
library(shinydashboard)
library(dygraphs)
library(magrittr)
library(xts)
library(timeSeries)
library(ggplot2)
library(DT)
library(rjson)
library(zoo)
library(scales)
library(shinycssloaders)
library(glue)
library(shinybusy)

########### UI Component Begins #############
withMathJax()
ui<- 
  fluidPage(
  conditionalPanel(
    condition = "input.password != 'nov@18'",  
    #textInput("username", "Username:", value = "Type the username here"),
    textInput("password", "Password:", value = "Type the password here")
  ),
  conditionalPanel(
  condition = "input.password == 'nov@18'",
  add_busy_spinner(spin = "fading-circle"),
  dashboardPage(skin = "green",
  dashboardHeader(title = "Shell - PAM"),
  dashboardSidebar(
    sidebarMenu(id = "tabs",
                style = "position: fixed; overflow: visible;",
                menuItem("KPI-Dashboard", tabName = "one", icon = icon("dashboard")),
                menuItem("Prediction", tabName = "six", icon = icon("chart-line")),
                menuItem("Configuration", tabName = "seven", icon = icon("chart-line")),
                menuItem("Model Evaluation", tabName = "ten", icon = icon("chart-line")),
                menuItem("Process Analysis", tabName = "eleven", icon = icon("chart-line"))
                )
    ),
  dashboardBody(
    tags$head(tags$style(HTML('.myClass{font-size: 20px;line-height: 50px;text-align: left;font-family: "Georgia";padding: 0 15px;overflow: hidden;color: white;}'))),
    tags$script(HTML('$(document).ready(function() {$("header").find("nav").append(\'<span class="myClass"> Predictive Maintenance Admin Console for BSP champion 7-Control Valves</span>\');})')),
    tags$head(tags$style(HTML('
        /* logo */
                              .skin-green .main-header .logo {
                              background-color: #bf1801;
                              position: fixed;
                              }
                              
                              /* logo when hovered */
                              .skin-green .main-header .logo:hover {
                              background-color: #bf1801;
                              }
                              
                              
                              /* navbar (rest of the header) */
                              .skin-blue .main-header {
                              position: fixed;
                              overflow: true
                              }        
                              /* toggle button when hovered   */                   
                              .skin-blue .main-header .navbar .sidebar-toggle:hover{
                              background-color: #14b74a;
                              }
                              '))),
    tabItems(
      tabItem(tabName = "one",
              fluidRow(box(title = "Overview", solidHeader = TRUE, width = 20, valueBoxOutput("Green"), valueBoxOutput("Red"), valueBoxOutput("Yellow"))),
              fluidRow(lapply(1:total_boxes, function(i) {infoBoxOutput(paste0('IFBox', i))}))
             ),
      tabItem(tabName = "six",
              h2("Valves Prediction Analysis"),
              fluidRow(
                box(
                  selectInput("ModelSelector", 
                              label = h4("Select Valve"), 
                              choices = NULL)
                ),
                box(sliderInput("TopActors", 
                              "Select Top Variables Contributes to the Prediction, to view in the plot",
                              min = 0, max = 10, value = 0))
                ),
              fluidRow(
                dygraphOutput("actual_vs_predict_gph", height =280),
                dygraphOutput("deviation_gph",height = 200),
                dygraphOutput("alarm_gph",height = 200),
                dygraphOutput("mode_gph",height = 200)
                )
              ),
      tabItem(
        tabName = "ten",
        fluidRow(column(5, box(selectInput("ModelSelector1", label = h4("Select valve"), choices = NULL, width = "300px",))),
          box(
          column(5, dateRangeInput("daterange_tr", label= "Selected Model Training Period", start = "2018-06-10", end = "2019-01-31")),
          column(5, dateRangeInput("daterange_te", label = "Period to assess Quality of the Model", start = "2019-02-01", end = "2019-06-30"))
          )
          ),
        fluidRow(
          box(title = 'Help Text to understand KPI', solidHeader = TRUE, width = 15 , collapsible = TRUE, collapsed = TRUE,
              column(12, helpText('RMSE: It represents the sample standard deviation of the differences between predicted values and observed values (called residuals)
                                  .\n It measures the error rate of the Model. Lower the value, Better Model. Zero RMSE means perfect model') ),
              
              column(12, helpText('MAE: MAE is the average of the absolute difference between the predicted values and observed value
                                  .\n It measures the error rate of the Model. Lower the value, Better Model. Zero MAE means perfect model') ),
              
              column(12, helpText('R2: R Squared is often used for explanatory purposes and explains how well your selected independent variable(s)
                                  explain the variability in your dependent variable(s).
                                   \n Closer to one, Better the Model')),
              column(4, uiOutput("url_rmse")),column(4, uiOutput("url_mae")),column(4, uiOutput("url_r2")),
              
              fluidRow(img(src= "abc.png", height="20%", width="30%", align="left"),img(src= "mae.png", height="20%", width="30%", align="center"),
                       img(src = "r2.png", height="20%", width="30%", align="right"))), 
            
          box(title = "Training KPI", solidHeader = TRUE, width = 15 ,valueBoxOutput('tr_MSE'), valueBoxOutput('tr_MAE'), valueBoxOutput('tr_R2')
          )
        ,
          box(
            title = "Testing KPI", solidHeader = TRUE, width = 15,valueBoxOutput('te_MSE'), valueBoxOutput('te_MAE'), valueBoxOutput('te_R2')
          )
        ),
        fluidRow(
        box( title = "PI Tags Identified by the Model for Prediction of Valve Opening", solideHeader= TRUE,
             helpText("Note: Operating Range of the Tags- Mean and Range Values "),
             shiny::dataTableOutput('table')),
        
        box( title = "Model Prediction Equation developed by Machine Learning Algorithm", solidHeader = TRUE,
             helpText("Note: PI Tags used in this Equation will be normalized using the Historical Statistical Information(Mean and Range)"),
             textOutput("equation")
        )
        ),
        fluidRow(
            box(title = 'Help Text to understand Residual Plots', solidHeader = TRUE, width = 15 , collapsible = TRUE, collapsed = TRUE,
                column(12,helpText("If Visible Patterns are observed in these Plots, indicates Model is biased and needs Modifications")),
                column(6,uiOutput("url_res"))),
            box(title = "Training Period",column(12,withSpinner(plotOutput("ResidualPlot_tr"))),collapsible=TRUE,collapsed =TRUE),
            box(title = "Testing Period",column(12,withSpinner(plotOutput("ResidualPlot_te"))),collapsible=TRUE,collapsed =TRUE)
          ),
        fluidRow(
          box(solidHeader = TRUE, width = 20,
            sliderInput("bins_tr", label = "Select the Bins for Histogram", min = 0, max = 100, step = 5, value = 10, width = '1500px')
          )
        ),
        fluidRow(
          box(title = "Fraction of Valve Opening",column(12,withSpinner(plotOutput("histplot_tr"))),collapsible=TRUE,collapsed =TRUE ),
          box(title = "Fraction of Valve Opening",column(12,withSpinner(plotOutput("histplot_te"))),collapsible=TRUE,collapsed =TRUE)
                )
        ),
      tabItem(tabName = "seven",
              fluidRow(box(title = "Select a Control Valve to Create/Modify Model Parameters", status = "primary", solidHeader = TRUE, width = 20,
                           column(6, selectInput("new_valve", label="Select Valve Output PI Tag", choices = "")),
                           box(title = "Model Status", status = "info",  column(6, textOutput("valve_info")))

              )),
              fluidRow(box(title = "Attributes",solidHeader = TRUE, width = 20, status = "primary", collapsible = TRUE, collapsed = FALSE,
                           box(width=6, status = "info", column(6,textInput("valveplant_textinput", label = "Plant" ,  value = "", width = "300px"))),
                           box(width=6, status = "info", column(6,textInput("Location_textinput", label = "Location" ,  value = "", width = "1500px"))),
                           box(width=8, status = "info", column(8,textInput("description_textinput", label = "Description" ,  value = "", width = "1500px"))),
                           box(width=4, status = "info", column(4,textInput("type_textinput", label = "Type" ,  value = "", width = "300px" )))
                           )),
              
              fluidRow(box(title = "Model Attributes",
                           solidHeader = TRUE, width = 20, status = "primary", collapsible = TRUE, collapsed = FALSE,
                           
                           box(title = "Select a Time period to where the Valve Operating Normally to Train the Model",
                               width=6, status = "info", column(4,dateInput("trstart_textinput", label = "Period Start" ,  value = "", width = "200px" ))
                                                       , column(4,dateInput("trend_textinput", label = "Period End" ,  value = "", width = "200px" ))),
                           
                           box(title = "Select a Time period to Test the Performance of the Trained Model", 
                               width=6, status = "info", column(4,dateInput("testart_textinput", label = "Period Start" ,  value = "", width = "200px" ))
                                                       , column(4,dateInput("teend_textinput", label = "Period End" ,  value = "", width = "200px" ))),
                           
                           box(width=4, status = "info", column(4,selectInput("algo", label = "Choose the Machine Learning Algorithm to Train" ,
                                                                              choices = c("Ridge","Lasso","Elastic-Net","Random Forest","Lasso-Ridge"), width = "300px" ))),
                           
                           box(width=8, status = "info",
                               helpText("Note: Higher the number, Better the quality and increase in Compute time. (Recommended : 50)"),
                               column(12,sliderInput("maxfeature",label = "Select the number of features required for model.",
                                                     min = 0, max = 500, step = 10, value = 50, width = "1800px" )))
                           )),
              
              
              fluidRow(box(title = "Define Valve Modes of operation to improve the Model Qaulity- Optional",
                           solidHeader = TRUE, width = 20, status = "primary", collapsible = TRUE, collapsed = TRUE,
                           column(4,selectInput("modepitag", label = "Mode PI Tag" , choices = "", width = "300px" )),
                           box(width=4, status = "info", column(4,selectInput("filtercond", label = "Condition" ,  choices = c(">","<","=",">=","<=","","!="), width = "300px" ))),
                           box(width=4, status = "info", column(4,textInput("filterpitag", label = "Value" ,  value = "", width = "300px" )))
                      )),
              
              
              
              fluidRow(box(title = "Additional Information to reduce Bias in the Model Performance", solidHeader = TRUE, width = 20, status = "primary", collapsible = TRUE, collapsed = FALSE,
                           fluidRow(column(6,selectInput("exclusiontag", label = "List of Tags Potentially Impacting the Quality of the Model  " ,
                                                         choices = "", width = "300px", multiple = TRUE )),
                                    column(6,selectInput("inclusiontag", label = "Mandatory Tags for the Model- Inclusion List" , 
                                                         choices = "", width = "300px", multiple = TRUE ))),
                           
                       fluidRow(box(title = "Lower and Upper Range valve Operation to Eliminate Non-realistic Values",
                                    width=12, status = "info", column(6,textInput("bplower", label = "Band pass lower limit" ,  value = "", width = "300px" )),
                                    column(6,textInput("bpupper", label = "Band pass upper limit" ,  value = "", width = "300px" ))))
              )),
              fluidRow(box(title = "Define Alarm Criteria",solidHeader = TRUE, width = 20, status = "primary", collapsible = TRUE, collapsed = FALSE,
                           column(12,helpText("NOTE: Alarm Will be TRIGGERED when the DIFFERENCE between the actual valve opening and predicted valve opening is above the
                                              DEVIATION THRESHOLD for consecutive number of points ABOVE the ALARM TRIGGER value")),
                           column(12,helpText("Note: Alarm Will be STOPPED when the DIFFERENCE between the actual valve opening and predicted valve opening is below the
                                              DEVIATION THRESHOLD for consecutive number of points ABOVE the ALARM STOP value")),
                           box(width=4, status = "info", column(4,textInput("deviation_thres", label = "Deviation Threshold" ,  value = "", width = "300px" ))),
                           box(width=4, status = "info", column(4,textInput("alarm_trig", label = "Alarm Trigger" ,  value = "", width = "300px" ))),
                           box(width=4, status = "info", column(4,textInput("alarm_stop", label = "Alarm Stop" ,  value = "", width = "300px" )))
              )),
              fluidRow(box(title = "PI Server and Data Collection Details", solidHeader = TRUE, width = 20, status = "primary", collapsible = TRUE, collapsed = FALSE,
                           box(width=6, status = "info", column(4,textInput("piservername", label = "PI Server Name" ,  value = "", width = "600px" ))),
                           box(width=6, status = "info", column(4,textInput("interval", label = "Data Collection and Model Update Interval(Minutes)" ,  value = "", width = "600px" ))),
                           box(width=6, status = "info", column(4,textInput("pi_write_back_tag1", label = "Name of the PI Tag to store Model Predicted Valve Opening" ,  value = "", width = "600px" ))),
                           box(width=6, status = "info", column(4,textInput("pi_write_back_tag2", label = "Name of the PI Tag to store Model Alert Status" ,  value = "", width = "600px" )))
                           
              )),
              fluidRow(box(title = "Action Buttons", solidHeader = TRUE, width = 20, status = "primary", collapsible = TRUE, collapsed = FALSE,
                       box(title = "Create/Update Configuration", status = "primary", solidHeader = TRUE, width = 5, collapsible = TRUE, collapsed = TRUE, column(4,actionButton("create", "Create Config File"))),
                       box(title = "Train valve Model", solidHeader = TRUE, collapsible = TRUE, collapsed = TRUE, status = "primary", width = 5, column(4,actionButton("retrain", "Re-Train the Model"))),
                       box(title = "Update bat files", solidHeader = TRUE, width = 5, collapsible = TRUE, collapsed = TRUE, status = "primary", column(4,actionButton("updatebat", "Update bat files"))),
                       #box(title = "Tune Alarm Settings", solidHeader = TRUE, collapsible = TRUE, collapsed = TRUE, status = "primary", width = 5, column(4,actionButton("tune", "Re-Tune"))),
                       box(title = "Deploy Valve", solidHeader = TRUE, width = 5, collapsible = TRUE, collapsed = TRUE, status = "primary", column(4,actionButton("deploy", "Deploy")))
                       #box(title = "Delete Valve", solidHeader = TRUE, width = 5, collapsible = TRUE, collapsed = TRUE, status = "primary", column(4,actionButton("delete", "Delete")))
                       downloadButton("traininglog", "Check Training log"),
                       downloadButton("deploymentlog", "Check Deployment log")
                       ))
              ),
      
        tabItem(tabName = "eleven",
                fluidRow(box(title = "Tags Selection for Process and Flow Diagram ", status = "primary", solidHeader = TRUE, width = 20,
                             column(6, selectInput("flow_valve", label="Select Valve Opening Output Variable(%)", choices = "")),
                             column(6, selectInput("process_valve", label="Select Process Variable", choices = "")),
                             column(6, dateRangeInput("dr_flow", label= "Data Range Selection", start = "2017-06-01", end = "2019-04-30"))
                         )),
                fluidRow(box(title = "Select Y axis Metric and Color options", status = "primary", solidHeader = TRUE, width = 20,
                             column(6, radioButtons("log_normal",label = "Metric", choices = c("Log", "Normal"), selected = "Normal")),
                             column(6, radioButtons("color", label = "Color Metric", choices = c("Quarter","Month", "Week"), selected = "Quarter"))
                )),
                fluidRow(box(title = "Process Vs Valve Tag Relation", status = "primary", solidHeader = TRUE, width = 20,
                             helpText("Values in the Below Graphs are Normalized to the Range of (0,100)"),
                             column(12,withSpinner(plotOutput("scatter_process_flow"))),
                             column(12,withSpinner(dygraphOutput("process_timeseries", height =280))),
                             column(12,withSpinner(plotOutput("box_month")))))

               )
      
      )))))

################ R-Shiny UI- Code Ends ###############
