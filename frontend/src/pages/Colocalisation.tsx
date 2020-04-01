import React, {useState, useReducer } from "react";
import { makeStyles} from '@material-ui/core/styles';

import Button from '@material-ui/core/Button';
import Typography from "@material-ui/core/Typography";
import Paper from '@material-ui/core/Paper';
import Grid from '@material-ui/core/Grid';
import TextField from '@material-ui/core/TextField';
import ListItem from '@material-ui/core/ListItem';
import ListItemText from '@material-ui/core/ListItemText';
import List from '@material-ui/core/List';
import InputLabel from '@material-ui/core/InputLabel';
import MenuItem from '@material-ui/core/MenuItem';
import FormHelperText from '@material-ui/core/FormHelperText';
import FormControl from '@material-ui/core/FormControl';
import Select from '@material-ui/core/Select';
import { stat } from "fs";
import fetch from 'isomorphic-fetch';
import { ThemeProvider } from '@material-ui/styles';
import TopContent from "../components/TopContent";
import Stepper from '@material-ui/core/Stepper';
import Step from '@material-ui/core/Step';
import StepLabel from '@material-ui/core/StepLabel';

// const projectTheme = theme;
const useStyles = makeStyles(theme => ({
    root: {
      maxWidth: 800,
      paddingAbove: 7,
      
    },
    textBoxes: {
        maxWidth: 300,
        padding: 8
    },
    bullet: {
      display: 'inline-block',
      margin: '0 2px',
      transform: 'scale(0.8)',
    },
    title: {
      fontSize: 14,
    },
    pos: {
      marginBottom: 12,
    },
    center: {
        display: 'flex',
        width: '100%',
        justifyContent: 'center',
    },
    box:{
        padding: 15,
    },
    inputs: {
        '& .MuiTextField-root': {
            margin: theme.spacing(2),
            width: '25ch'}
    
    },
    paper: {
        padding: 10,
        textAlign: 'center',
        backgroundColor: 'white'
    },
    formControl: {
        margin: 10,
        minWidth: 150,
      },
    items: {
        textAlign: "left",
        justifyContent: "left"
    },
    colocTitle: {
        textAlign: "left",
        margin: 10,
    },
    backButton: {
        marginRight: theme.spacing(1),
      },
      instructions: {
        marginTop: theme.spacing(1),
        marginBottom: theme.spacing(1),
      },
   
  }));
  

const TextInput = (props: any) =>{
    const classes = useStyles();
    return(
        <TextField
            className={classes.inputs}
            id="standard-textarea"
            label={props.label}
            variant="outlined"
            onChange={props.onChange}
            value={props.value}
        />
    );
}

export function NumericalInput(props: any){
    const classes = useStyles();
    return(
        <TextField  
            className={classes.inputs}
            id="standard-number"
            label={props.label}
            type="number"
            onChange={props.onChange}
            inputProps={props.inputProps}
            variant="outlined"
            value={props.value}
        />
    );
}


export function ColocalisationParameters(props: any) {
    const inputProps = {
        step: 0.01,
        min: 0.00
      };
    const classes = useStyles();
    return (
        <div>
        <form className={classes.inputs} noValidate autoComplete="off">
            
            <NumericalInput  
                className={classes.textBoxes}   
                label="x-y resolution"
                inputProps={inputProps}
                onChange={
                    (event: any) => {
                        console.log(event.target.value)
                        props.onConfigChange({
                            type: "xy_resolution", 
                            value: event.target.value,
                            cast: "number"});
                    }
                }
                value={props.config["xy_resolution"]}
                
            />
            <NumericalInput   
                className={classes.textBoxes}
                label="z resolution"
                inputProps={inputProps}
                onChange={
                    (event: any) => {
                        console.log(event.target.value)
                        props.onConfigChange({
                            type: "z_resolution", 
                            value: event.target.value,
                            cast: "number"});
                    }
                }
                value={props.config["z_resolution"]}
            />
            <NumericalInput  
                className={classes.textBoxes} 
                label="Min overlap"
                inputProps={inputProps}
                onChange={
                    (event: any) => {
                        console.log(event.target.value)
                        props.onConfigChange({
                            type: "min_overlap", 
                            value: event.target.value,
                            cast: "number"});
                    }
                }
                value={props.config["min_overlap"]}
            />
            <NumericalInput 
                className={classes.textBoxes}
                classes={classes}    
                label="Max distance"
                inputProps={inputProps}
                onChange={
                    (event: any) => {
                        console.log(event.target.value)
                        props.onConfigChange({
                            type: "max_distance",
                            value: event.target.value,
                            cast: "number"});
                    }
                }
                value={props.config["max_distance"]}
            />
        </form>
        </div>
    );                
}


const RenderChannelList = (props: any) => { 
    console.log(props.items)
    return (
        <div>
            {Object.keys(props.items).map((item: any, index: any) => {
                const colocalisationObject = props.items[item];
                console.log(colocalisationObject)
                return (
                <ListItem key={index}>
                    <ListItemText 
                    primary={item}
                    secondary={<React.Fragment>
                        <RenderColocalisation 
                    channel={item}
                    classes={props.classes} 
                    channels={colocalisationObject}
                    onChange={props.onChange}
                    val={index}
                    state={props.state}
                    />
                    </React.Fragment>} />
                </ListItem>
            )})}
        </div>
    );
}

const RenderColocalisation = (props: any) => {
    const coloclalisationTypes = ["Distance", "Overlap", "None"];
    const [coloc, setColoc] = useState(props.channels);
    const handleFormSelection = (event: React.ChangeEvent<{ value: unknown }>) => {
        setColoc(event.target.value as string);
    };
    
    return (
        <div>
            {Object.keys(props.channels).map((item:any, index: any) => (
                <div key={index}>
                <FormControl className={props.classes.inputs}>
                    <InputLabel  id="demo-simple-select-label">{item}</InputLabel>
                    <Select
                        labelId="demo-simple-select-label"
                        id="demo-simple-select"
                        onChange={
                            (event: any) => {
                                props.onChange({channel: props.channel, coloc: item, value: event.target.value})
                            }
                        }
                        value={props.state[props.channel][coloc]}
                    >
                        {coloclalisationTypes.map((item: any, index: any) => (
                            <MenuItem key={index} value={item}>{item}</MenuItem>
                        ))}
                    </Select>
                </FormControl>
                </div>
            ))}
        </div>
    );
}


const createColocalisationObject = (channels: Array<string>) => {
    const colocalisationObject = {} as any;
    for (var i = 0; i < channels.length; i++) {
        const channelName  = channels[i];
        colocalisationObject[channelName] = createChannelColocalisationObject(channels, i);
      }
    return colocalisationObject;
}

const createChannelColocalisationObject = (channels: Array<string>, channelIndex: number) => {
    const channelColocalisationObject = {} as any;
    for (var i = 0; i<channels.length; i++){
        if(i===channelIndex) continue;
        channelColocalisationObject[channels[i]] = "None";
    }
    return channelColocalisationObject;
}

 const ColocalisationTypes = (props: any) =>{ 
    console.log(props.state)
    return (
        <div>
            <Typography variant="h5" className={props.classes.colocTitle}> You have selected the following channels:</Typography>
            
            <List>
                <RenderChannelList 
                classes={props.classes} 
                items={props.items}
                onChange={props.onChange}
                state={props.state}/>
            </List>
        </div>
    );
}

export function NavigationButton(props: any){
    return (
        <Button
            variant="contained"
            color="primary"
            onClick={props.clickFunction}
            >
            {props.label}
        </Button>
    );
}

const ColocalisationGetStarted = (props: any) => {
    return (
        <Grid
            container
            direction="column"
            justify="flex-start"
            alignItems="center"
            spacing={2}
            >
                <Typography 
                    variant="h5">
                    Welcome to the colocalisation module! ⭕
                </Typography>
                <Typography 
                    variant="h6">
                    Here you will find all the wonderful things related to the module.
                </Typography>
        </Grid>
    );

}

const ColocalisationInputs = (props: any) => {
    return (
        <div>
        <form className={props.classes.inputs} noValidate autoComplete="off">
            <TextInput
                label="Input directory"
                onChange={
                    (event: any) => {
                        console.log(event.target.value)
                        props.onConfigChange({
                            type: "input_dir", 
                            value: event.target.value
                            });
                    }
                }
                value={props.config["input_dir"]}
            />
            <TextInput
                label="Output directory"
                onChange={
                    (event: any) => {
                        console.log(event.target.value)
                        props.onConfigChange({
                            type: "output_dir", 
                            value: event.target.value
                            });
                    }
                }
                value={props.config["output_dir"]}
            />
            <TextInput
                label="Output filename"
                onChange={
                    (event: any) => {
                        console.log(event.target.value)
                        props.onConfigChange({
                            type: "output_filename", 
                            value: event.target.value
                            });
                    }
                }
                value={props.config["output_filename"]}
            />
            <TextInput
                label="Channels"
                onChange={props.onChannelChange}
                value={props.channels}
            />

        </form>
        </div>
    )
}

const ColocalisationConfirmation = (props: any) => {
    return (
        <div>
            <Typography variant="h4">Is everything correct?</ Typography>
            <Typography variant="h5">Input directory: {props.config["input_dir"]}</Typography>
            <Typography variant="h5">Output directory: {props.config["output_dir"]}</Typography>
            <Typography variant="h5">Output filename: {props.config["output_filename"]}</Typography>
            <Typography variant="h5">x-y resolution: {props.config["xy_resolution"]}</Typography>
            <Typography variant="h5">z resolution: {props.config["z_resolution"]}</Typography>
            <Typography variant="h5">Min overlap: {props.config["min_overlap"]}</Typography>
            <Typography variant="h5">Max distance: {props.config["max_distance"]}</Typography>
        </div>
    );
}

const ColocalisationRunning = (props: any) => {
    return (
        <Typography variant="h5">Your job has been submitted!</Typography>
    );
}


function getSteps() {
    return [
        'Getting started', 
        'Inputs and outputs',
        'How do you want to colocalise?', 
        'Colocalisation parameters', 
        'Is everything ok?',
        'Running!' ];
    };
    
      
     
      
    export  function HorizontalLabelPositionBelowStepper() {
    const classes = useStyles();

    // Handling steps
    const [activeStep, setActiveStep] = React.useState(0);
    const steps = getSteps();
    
    const handleNext = () => {
        if(activeStep==1){
            channelsDispatch({channel: "init", coloc: "", value: initialChannelList});
            
        }
        else if(activeStep==2){
            dispatch({type: "channels", value: channelsState, cast: ""});
        }
        else if(activeStep==4){
            postConfig();
        }
        setActiveStep((prevActiveStep) => prevActiveStep + 1);
        
    };

    const handleBack = () => {
        setActiveStep((prevActiveStep) => prevActiveStep - 1);
    };
    
    const handleReset = () => {
        setActiveStep(0);
    };

    // Handling config update   

    const initialConfig = {
        input_dir: "",
        output_dir: "",
        output_filename: "",
        channels: [],
        xy_resolution: null,
        z_resolution: null,
        min_overlap: null,
        max_distance: null
    }; 
    console.log(initialConfig);
    
    
    const reducer = (state: any, action: {type: string, value: any, cast: string}) => {
        console.log(state);
        return {...state, [action.type]: action.value};

    };

    const [configState, dispatch] = useReducer(reducer, initialConfig);

    console.log(configState);

    // channel handling
    const [channels, setChannels] = useState("")
    const handleChannelChange = (e: any) => {
        const value = e.target.value
        setChannels(value)
    }
    const channelList = channels.split(" ");

    const initialChannelList = createColocalisationObject(channelList);
    const initialChannelState = {} as any;
    
    const channelsReducer = (state: any, action: {channel: string, coloc: string,  value: any}) => {
        if(action.channel === "init"){
            return action.value;
        }
        else {
            state[action.channel][action.coloc] = action.value;
            console.log(state);
            return {...state, [action.channel]:
                {...state[action.channel], [action.coloc]: action.value}
            };
        }

    };
    const [channelsState, channelsDispatch] = useReducer(channelsReducer, initialChannelState);
    console.log(channelsState);

    
    const postConfig = () => {
        console.log("doign soemthign")
                    return fetch('http://127.0.0.1:5000/', {
                    method: 'POST',
                    body: JSON.stringify(configState),
                    headers: {
                        'Content-Type': 'application/json'
                    },
                }).then((res: any) => {
                    return res;
                }).catch((err: any) => err)}
    let stepperContent;
    switch (activeStep){
        case 0:
            stepperContent =  (<ColocalisationGetStarted/>);
            break;
        case 1:
            stepperContent =  (
                <ColocalisationInputs 
                    classes={classes}
                    onConfigChange={dispatch} 
                    onChannelChange={handleChannelChange} 
                    config={configState}
                    channels={channels}
                />);
            break;
        case 2:
            stepperContent =  (<ColocalisationTypes
                className={classes.items}
                classes={classes} 
                channelList={channelList}
                onChange={channelsDispatch}
                state={channelsState}
                items={initialChannelList}
            
                />);
            break;
        case 3:
            stepperContent =  (
            <ColocalisationParameters
                onConfigChange={dispatch} 
                onChannelChange={handleChannelChange} 
                config={configState}
                channels={channels}
            />);
            break;
        case 4: 
            stepperContent =  (<ColocalisationConfirmation config={configState} />);
            break;
        case 5:
            stepperContent = (<ColocalisationRunning/>);
            break;
        default:
            stepperContent = (<ColocalisationGetStarted/>);
    }


    
    
    return (
        <div className={classes.root}>
        <Stepper activeStep={activeStep} alternativeLabel>
            {steps.map((label) => (
            <Step key={label}>
                <StepLabel>{label}</StepLabel>
            </Step>
            ))}
        </Stepper>
        <div>
            {activeStep === steps.length ? (
            <div>
                {stepperContent}
                }
                <Button onClick={handleReset}>Reset</Button>
            </div>
            ) : (
            <div>
                {stepperContent}
                <div>
                <Button
                    disabled={activeStep === 0}
                    onClick={handleBack}
                    className={classes.backButton}
                >
                    Back
                </Button>
                <Button variant="contained" color="primary" onClick={handleNext}>
                    {activeStep === steps.length - 1 ? 'Finish' : 'Next'}
                </Button>
                </div>
            </div>
            )}
        </div>
        </div>
    );
    }

    export const Colocalisation = (props: any) => {
        return(
            <TopContent>
                <HorizontalLabelPositionBelowStepper/>
            </TopContent>
        );
    }


