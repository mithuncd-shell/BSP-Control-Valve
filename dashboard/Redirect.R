library(shiny)
options(shiny.port = 9999)
runApp(appDir = "C:\\PAM\\bsp_control_valve\\Code\\dashboard", port = getOption("shiny.port"),
       launch.browser = getOption("shiny.launch.browser", interactive()),
       host = getOption("shiny.host", "0.0.0.0"), workerId = "",
       quiet = FALSE, display.mode = c("auto", "normal", "showcase"),
       test.mode = getOption("shiny.testmode", FALSE))