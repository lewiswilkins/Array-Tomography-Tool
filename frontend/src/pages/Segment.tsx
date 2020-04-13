import React from "react";
import TopContent from "../components/TopContent";
import {
  Typography,
  makeStyles,
} from "@material-ui/core";
import fetch from 'isomorphic-fetch';

const useStyles = makeStyles(theme => ({
  text: {
    textAlign: "left",
  }
}));

const bokehTest = async () => {
  const log = await fetch(
    `http://127.0.0.1:5000/bokeh_test/`, {
      method: 'GET',
      mode: 'cors', 
      cache: 'no-cache',
      headers: {
          'Access-Control-Allow-Origin':'',
      },
  });
  const data = await log.json();
  console.log(data);

  return (data);
}





export const Segment =  (props: any) => {
  const styles = useStyles();
  const [bokeh, setData] = React.useState({url: "", script_id: ""});

  React.useEffect(() => {
    bokehTest().then(setData);
  }, []);
  
  React.useEffect(() => {
    const script = document.createElement('script');
    script.async = true;
    script.src = bokeh.url;
    script.id = bokeh.script_id;

    document.body.appendChild(script);
    return () => {
      document.body.removeChild(script);
    }
  }, []);


  return (
    <TopContent>
      <Typography 
        className={styles.text}
        variant="h5">
          Welcome to the segment module! 🍰
      </Typography>
      <Typography 
        className={styles.text}
        variant="h6">
          Here you will find all the wonderful things related to the module.
      </Typography>
      
    </TopContent>
  );
};