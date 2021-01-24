import React from "react";
import { BrowserRouter as Router, Switch, Route } from "react-router-dom";
import { ThemeProvider } from "@material-ui/core/styles";
import Home from "./pages/Home/Home";
import AddApplication from "./pages/AddApplication/AddApplication";
import RemoveApplication from "./pages/RemoveApplication/RemoveApplication";
import ManageCategory from "./pages/ManageCategory/ManageCategory";
import ManageControlMode from "./pages/ManageControlMode/ManageControlMode";
import FaqAndHelp from "./pages/FaqAndHelp/FaqAndHelp";
import Error404 from "./pages/404/404";
import theme from "./constants/Theme";

const App = (props) => {
  return (
    <ThemeProvider theme={theme}>
      <Router>
        <Switch>
          <Route path="/" exact component={Home} />
          <Route path="/addApplication" component={AddApplication} />
          <Route path="/removeApplication" component={RemoveApplication} />
          <Route path="/manageCategory" component={ManageCategory} />
          <Route path="/manageControlMode" component={ManageControlMode} />
          <Route path="/faqAndHelp" component={FaqAndHelp} />
          <Route path="*" component={Error404} />
        </Switch>
      </Router>
    </ThemeProvider>
  );
};

export default App;
