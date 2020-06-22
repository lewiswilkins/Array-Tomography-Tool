import React from "react";
import { makeStyles } from '@material-ui/core/styles';
import {
    Paper,
    Grid
  } from "@material-ui/core";


  const useStyles = makeStyles(theme => ({
    root: {
      flexGrow: 1,
      width: '100%',
    },
    paper: {
      maxWidth: '100%',
      margin: `${theme.spacing(1)}px auto`,
      padding: theme.spacing(3),
    },
    text: {
      textAlign: "left",
    }
  }));
  

const TopContent: React.FC = ({ children }) => {
    const styles = useStyles();
    return (
        <Paper className={styles.paper} elevation={3} >
            <Grid
                container
                direction="column"
                justify="space-evenly"
                alignItems="center"
            >
                <Grid item>
                    {children}
                </Grid>
            </Grid>
        </Paper>
    );
}

export default TopContent;
