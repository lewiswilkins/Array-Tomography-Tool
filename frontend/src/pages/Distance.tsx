import React from "react";
import TopContent from "../components/TopContent";
import {
  Typography,
  makeStyles,
} from "@material-ui/core";


const useStyles = makeStyles(theme => ({
  text: {
    textAlign: "left",
  }
}));

export const Distance =  (props: any) => {
  const styles = useStyles();

  return (
    <TopContent>
      <Typography 
        className={styles.text}
        variant="h5">
          Welcome to the plaque distance module! 🍽️
      </Typography>
      <Typography 
        className={styles.text}
        variant="h6">
          Here you will find all the wonderful things related to the module.
      </Typography>
    </TopContent>
  );
};