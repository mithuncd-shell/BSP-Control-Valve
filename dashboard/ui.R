################ Packages Required ###########
library(shiny)
library(shinydashboard)
library(dygraphs)
library(magrittr)
library(xts)
library(timeSeries)
########### UI Component Begins #############
ui<- dashboardPage(skin = "green",
  dashboardHeader(title = "Shell - PAM"),
  dashboardSidebar(
    sidebarMenu(id = "tabs",
                style = "position: fixed; overflow: visible;",
                menuItem("KPI-Dashboard", tabName = "one", icon = icon("dashboard")),
                menuItem("Prediction", tabName = "six", icon = icon("chart-line"))
                )
    ),
  dashboardBody(
    tags$head(tags$style(HTML('.myClass{font-size: 20px;line-height: 50px;text-align: left;font-family: "Georgia";padding: 0 15px;overflow: hidden;color: white;}'))),
    tags$script(HTML('$(document).ready(function() {$("header").find("nav").append(\'<span class="myClass"> Predictive Maintenance Dashboard for BSP - Champion7-Control Valves</span>\');})')),
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
              )
            )
      )
)
################ R-Shiny UI- Code Ends ###############
