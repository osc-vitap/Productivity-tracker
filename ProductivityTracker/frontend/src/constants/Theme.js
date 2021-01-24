import { createMuiTheme } from "@material-ui/core/styles";

const theme = createMuiTheme({
  palette: {
    primary: {
      main: "#12005E",
      light: "#2500C0",
      dark: "#0D0045",
    },
    secondary: {
      main: "#e93651",
      light: "#f49ba8",
      dark: "#e30425",
    },
  },
  typography: {
    fontFamily: "'Montserrat', sans-serif",
  },
});

export default theme;
