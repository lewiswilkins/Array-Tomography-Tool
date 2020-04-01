import React from "react";
import Layout from "../components/Layout";
import styled from "styled-components";
import colors from "../config/colors";
import TopContent from "../components/TopContent";
import { Link, useHistory } from "react-router-dom";
import {
  Card,
  Paper,
  CardActionArea,
  Typography,
  CardContent,
  makeStyles,
  Grid
} from "@material-ui/core";

const Title = styled.h1`
  color: ${colors.primary};
  text-align: center;
`;

const useStyles = makeStyles(theme => ({
  root: {
    flexGrow: 1
  },
  paper: {
    maxWidth: 600,
    margin: `${theme.spacing(1)}px auto`,
    padding: theme.spacing(2),
  },
  text: {
    textAlign: "left",
  }
}));

export const Home =  (props: any) => {
  const styles = useStyles();

  return (
    <TopContent>
      <Typography 
        className={styles.text}
        variant="h5">
          Welcome to the Array Tomography Tool! 🔬
      </Typography>
      <Typography 
        className={styles.text}
        variant="h6">
          Here you will find all the wonderful things related to the tool.
      </Typography>
    </TopContent>
  );
};