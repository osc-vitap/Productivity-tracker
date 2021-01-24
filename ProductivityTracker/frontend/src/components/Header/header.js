import React from "react";
import { makeStyles } from "@material-ui/core/styles";
import AppBar from "@material-ui/core/AppBar";
import Toolbar from "@material-ui/core/Toolbar";
import Typography from "@material-ui/core/Typography";
import Button from "@material-ui/core/Button";
import IconButton from "@material-ui/core/IconButton";
import MenuIcon from "@material-ui/icons/Menu";
import HomeIcon from "@material-ui/icons/Home";
import Airplay from "@material-ui/icons/Airplay";
import DesktopAccessDisabledIcon from "@material-ui/icons/DesktopAccessDisabled";
import CategoryIcon from "@material-ui/icons/Category";
import ControlCameraIcon from "@material-ui/icons/ControlCamera";
import LiveHelpIcon from "@material-ui/icons/LiveHelp";
import styles from "./header.styles";
import SwipeableDrawer from "@material-ui/core/SwipeableDrawer";
import { List, ListItem, ListItemIcon, ListItemText } from "@material-ui/core";
import { Link } from "react-router-dom";

const useStyles = makeStyles((theme) => styles(theme));

const Header = (props) => {
  const classes = useStyles();

  const [drawerOpen, setDrawerOpen] = React.useState(false);

  const toggleDrawerState = () => {
    setDrawerOpen(!drawerOpen);
  };

  return (
    <div className={classes.root}>
      <AppBar position="fixed" className={classes.appBar}>
        <Toolbar>
          <IconButton
            edge="start"
            className={classes.menuButton}
            color="inherit"
            aria-label="menu"
            onClick={toggleDrawerState}
          >
            <MenuIcon />
          </IconButton>
          <Typography variant="h6" className={classes.title}>
            Productivity Tracker
          </Typography>
        </Toolbar>
      </AppBar>
      <SwipeableDrawer
        anchor="left"
        classes={{
          paper: classes.drawerPaper,
        }}
        className={classes.drawer}
        variant="temporary"
        open={drawerOpen}
        onClose={toggleDrawerState}
      >
        <div className={classes.drawerContainer}>
          <List>
            <ListItem
              onClick={toggleDrawerState}
              className={classes.content}
              component={Link}
              button
              to={"/"}
            >
              <ListItemIcon>
                <HomeIcon style={{ color: "#fff" }} />
              </ListItemIcon>
              <ListItemText primary="Dashboard" />
            </ListItem>
            <ListItem
              onClick={toggleDrawerState}
              className={classes.content}
              component={Link}
              button
              to={"/addApplication"}
            >
              <ListItemIcon>
                <Airplay style={{ color: "#fff" }} />
              </ListItemIcon>
              <ListItemText primary="Add Application" />
            </ListItem>
            <ListItem
              onClick={toggleDrawerState}
              className={classes.content}
              component={Link}
              button
              to={"/removeApplication"}
            >
              <ListItemIcon>
                <DesktopAccessDisabledIcon style={{ color: "#fff" }} />
              </ListItemIcon>
              <ListItemText primary="Remove Application" />
            </ListItem>
            <ListItem
              onClick={toggleDrawerState}
              className={classes.content}
              component={Link}
              button
              to={"/manageCategory"}
            >
              <ListItemIcon>
                <CategoryIcon style={{ color: "#fff" }} />
              </ListItemIcon>
              <ListItemText primary="Manage Category" />
            </ListItem>
            <ListItem
              onClick={toggleDrawerState}
              className={classes.content}
              component={Link}
              button
              to={"/manageControlMode"}
            >
              <ListItemIcon>
                <ControlCameraIcon style={{ color: "#fff" }} />
              </ListItemIcon>
              <ListItemText primary="Manage Control Mode" />
            </ListItem>
            <ListItem
              onClick={toggleDrawerState}
              className={classes.content}
              component={Link}
              button
              to={"/faqAndHelp"}
            >
              <ListItemIcon>
                <LiveHelpIcon style={{ color: "#fff" }} />
              </ListItemIcon>
              <ListItemText primary="FAQ's and Helps" />
            </ListItem>
          </List>
        </div>
      </SwipeableDrawer>
      <Toolbar />
    </div>
  );
};

export default Header;
