import React, { 
    useState,
    useEffect,
    useRef
 } from "react";
import {
    Card,
    CardContent,
    Typography,
    makeStyles
  } from "@material-ui/core";
import { getLog } from '../functions/fetchFunctions';
import useInterval from '@use-it/interval';

const useStyles = makeStyles({
    root: {
        minWidth: 275,
        minHeight: '300px',
        height: '300px',
        overflowY: 'scroll',
    },
    card: {
        minWidth: 275,
        minHeight: '300px',
    },
    consoleFont: {
        fontFamily: "Courier",
        margin: 0.1
    },
    p: {
        margin: -0
    }
  });


export const LogDisplay = (props: {jobId: string, parameter: string}) => {
    const classes = useStyles();
    const [logOutput, setLogOutput] = useState("");
    useInterval(() => {
        getLog(props.jobId, props.parameter).then(setLogOutput)
    }, 1000);

    const endRef = useRef(null)
    const scrollToBottom = () => {
        //@ts-ignore
        endRef.current.scrollIntoView({ behavior: "smooth" });
    }
    useEffect(scrollToBottom, [logOutput]);

    return (
    <div className={classes.root}>
        <Card>
            <CardContent>
                <Typography className={classes.consoleFont}>
                    {logOutput.split('\n').map ((item, i) => <p className ={classes.p} key={i}>{item}</p>)}
                    <div ref={endRef} />
                </Typography>
            </CardContent>
        </Card>
    </div>
    );
}