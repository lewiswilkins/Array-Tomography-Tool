import React from 'react';
import clsx from 'clsx';
import { makeStyles, useTheme, Theme, createStyles, createMuiTheme } from '@material-ui/core/styles';
import Drawer from '@material-ui/core/Drawer';
import CssBaseline from '@material-ui/core/CssBaseline';
import AppBar from '@material-ui/core/AppBar';
import Toolbar from '@material-ui/core/Toolbar';
import List from '@material-ui/core/List';
import Typography from '@material-ui/core/Typography';
import Divider from '@material-ui/core/Divider';
import IconButton from '@material-ui/core/IconButton';
import MenuIcon from '@material-ui/icons/Menu';
import ChevronLeftIcon from '@material-ui/icons/ChevronLeft';
import ChevronRightIcon from '@material-ui/icons/ChevronRight';
import ListItem from '@material-ui/core/ListItem';
import ListItemIcon from '@material-ui/core/ListItemIcon';
import ListItemText from '@material-ui/core/ListItemText';
import InboxIcon from '@material-ui/icons/MoveToInbox';
import MailIcon from '@material-ui/icons/Mail';
import { ThemeProvider } from '@material-ui/styles';
// import Router from "./bootstrap/Router";
import { useHistory } from "react-router-dom";
import FormatAlignCenterIcon from '@material-ui/icons/FormatAlignCenter';
import GrainIcon from '@material-ui/icons/Grain';
import OpacityIcon from '@material-ui/icons/Opacity';
import FiberSmartRecordIcon from '@material-ui/icons/FiberSmartRecord';
import LinearScaleIcon from '@material-ui/icons/LinearScale';
import HomeIcon from '@material-ui/icons/Home';
import {Colocalisation} from './pages/Colocalisation';
import {Home} from './pages/Home';
import {Distance} from "./pages/Distance";
import {Density} from "./pages/Density";
import {Alignment} from "./pages/Alignment";
import {Segment} from "./pages/Segment";



const drawerWidth = 240;

const useStyles = makeStyles((theme: Theme) =>
  createStyles({
    root: {
      display: 'flex',
    },
    appBar: {
      transition: theme.transitions.create(['margin', 'width'], {
        easing: theme.transitions.easing.sharp,
        duration: theme.transitions.duration.leavingScreen,
      }),
    },
    appBarShift: {
      width: `calc(100% - ${drawerWidth}px)`,
      marginLeft: drawerWidth,
      transition: theme.transitions.create(['margin', 'width'], {
        easing: theme.transitions.easing.easeOut,
        duration: theme.transitions.duration.enteringScreen,
      }),
    },
    menuButton: {
      marginRight: theme.spacing(2),
    },
    hide: {
      display: 'none',
    },
    drawer: {
      width: drawerWidth,
      flexShrink: 0,
    },
    drawerPaper: {
      width: drawerWidth,
    },
    drawerHeader: {
      display: 'flex',
      width: '80%',
      alignItems: 'center',
      padding: theme.spacing(0, 1),
      // necessary for content to be below app bar
      ...theme.mixins.toolbar,
      justifyContent: 'flex-end',
    },
    content: {
      flexGrow: 1,
      padding: theme.spacing(3),
      transition: theme.transitions.create('margin', {
        easing: theme.transitions.easing.sharp,
        duration: theme.transitions.duration.leavingScreen,
      }),
      marginLeft: -drawerWidth,
      
    },
    contentShift: {
      transition: theme.transitions.create('margin', {
        easing: theme.transitions.easing.easeOut,
        duration: theme.transitions.duration.enteringScreen,
      }),
      marginLeft: 0,
    },
    divider:{
      paddingLeft: theme.spacing(1)
    }
  }),
);

export const theme = createMuiTheme({
  palette: {
    primary: {
      light: '#82e9de',
      main: '#4db6ac',
      dark: '#82ada9',
      contrastText: '#fff',
    },
    secondary: {
      light: '#819ca9',
      main: '#546e7a',
      dark: '#29434e',
      contrastText: '#000',
    },
  },
  spacing: 8,

});




const getPageContent = (pageName: string) => {
  switch(pageName){
    case "home":
      return <Home/>;
    
    case "colocalisation":
      return <Colocalisation/>;

    default:
        return <Home/>;
  }
}



function App() {
  const classes = useStyles();
  // const history = useHistory();

  // Drawer hooks
  const [open, setOpen] = React.useState(false);
  const handleDrawerOpen = () => {
    setOpen(true);
  };
  const handleDrawerClose = () => {
    setOpen(false);
  };

  // Page hooks
  const [page, setPage] = React.useState(<Home/>);
  const handlePageChange = (pageComponent: any) => {
    setPage(pageComponent);
  };

 
  console.log(page);


  const processListIcons = [<FormatAlignCenterIcon/>,<GrainIcon/>];
  const processListPages = [<Alignment/>, <Segment/>];
  const analysisListIcons = [<OpacityIcon/>,<FiberSmartRecordIcon/>, <LinearScaleIcon/> ]
  const analysisListPages = [<Density/>,<Colocalisation/>, <Distance/> ]
  return (
    <ThemeProvider theme={theme}>
    <div className={classes.root}>
      <CssBaseline />
      <AppBar
        position="fixed"
        className={clsx(classes.appBar, {
          [classes.appBarShift]: open,
        })}
      >
        <Toolbar>
          <IconButton
            color="secondary"
            aria-label="open drawer"
            onClick={handleDrawerOpen}
            edge="start"
            className={clsx(classes.menuButton, open && classes.hide)}
          >
            <MenuIcon />
          </IconButton>
          <Typography variant="h6" noWrap>
           Array Tomography Tool
          </Typography>
        </Toolbar>
      </AppBar>
      <Drawer
        className={classes.drawer}
        variant="persistent"
        anchor="left"
        open={open}
        classes={{
          paper: classes.drawerPaper,
        }}
      >
        <div className={classes.drawerHeader}>
          <IconButton onClick={handleDrawerClose}>
            {theme.direction === 'ltr' ? <ChevronLeftIcon /> : <ChevronRightIcon />}
          </IconButton>
        </div>
        <List>
          <ListItem 
            button 
            key="home"
            onClick={()=> handlePageChange(<Home/>)}>
          <ListItemIcon><HomeIcon/></ListItemIcon>
            <ListItemText 
              primary="Home"
              />
          </ListItem>
        </List>
        <Divider />
        <div className={classes.divider}>
        <Typography
          color="secondary"
          display="block"
          variant="caption"
        >
          Processing
        </Typography>
        </div>
        <List>
      {['Alignment', 'Segment'].map((text, index) => (
            <ListItem 
              button 
              key={text}
              onClick={()=> handlePageChange(processListPages[index])}>
              <ListItemIcon>{processListIcons[index]}</ListItemIcon>
              <ListItemText 
                primary={text}
              />
            </ListItem>
          ))}
        </List>
        <Divider />
        <div className={classes.divider}>
        <Typography
          color="secondary"
          display="block"
          variant="caption"
        >
          Analysis
        </Typography>
        </div>
        <List>
          {['Density', 'Colocalisation', 'Plaque Distance'].map((text, index) => (
            <ListItem 
              button 
              key={text}
              onClick={()=> handlePageChange(analysisListPages[index])}>
              <ListItemIcon>{analysisListIcons[index]}</ListItemIcon>
              <ListItemText primary={text} />
            </ListItem>
          ))}
        </List>
      </Drawer>
      <main
        className={clsx(classes.content, {
          [classes.contentShift]: open,
        })}
      >
        <div className={classes.drawerHeader} />
        {page}
      </main>
      
      
    </div>
    </ThemeProvider>
  );
}

export default App;