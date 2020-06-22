import React, { 
  useState,
  useEffect,
  useReducer,

} from "react";
import TopContent from "../components/TopContent";
import {
  Typography,
  makeStyles,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Button,
  Grid,
  Stepper,
  StepLabel,
  Step,
} from "@material-ui/core";
import { postConfig, getLog } from '../functions/fetchFunctions';
import { configReducer } from '../hooks/configReducer';
import { ParameterTable } from '../components/ParameterTable';
import { TextInput, NumericalInput } from '../components/Inputs';
import { LogDisplay } from '../components/LogDisplay';

const useStyles = makeStyles(theme => ({
  text: {
    textAlign: "left",
  },
  stepperContent: {
    padding: theme.spacing(2)
  },
  backButton: {
    marginRight: theme.spacing(1),
  },
  stepper: {
    width: '100%',
  },
  inputs: {
    '& .MuiTextField-root': {
        margin: theme.spacing(2),
        width: '25ch'}
  },

}));

const AlignmentGetStarted = (props: any) => {
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
                Welcome to the alignment module! 📐
            </Typography>
            <Typography 
              variant="h6">
                Here you will find all the wonderful things related to the module.
          </Typography>
      </Grid>
  );
}

const AlignmentInputs = (
  props: {
    classes: any, config: {
      input_dir: string, output_dir: string, channels: Array<string>, alignment_channel: string
    }, onConfigChange: any
  }
  ) => {
  return (
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
                value={props.config.input_dir}
                classes={props.classes}
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
                value={props.config.output_dir}
                classes={props.classes}
            />
            <TextInput
                label="Channels"
                onChange={
                  (event: any) => {
                      console.log(event.target.value)
                      props.onConfigChange({
                          type: "channels", 
                          value: event.target.value.split(" ")
                          });
                  }
              }
                value={props.config.channels.join(" ")}
                classes={props.classes}
            />
            <TextInput
                label="Alignment channel"
                onChange={
                    (event: any) => {
                        console.log(event.target.value)
                        props.onConfigChange({
                            type: "alignment_channel", 
                            value: event.target.value
                            });
                    }
                }
                value={props.config.alignment_channel}
                classes={props.classes}
            />
        </form>
  );
}

const AlignmentConfirmation = (props: {classes: any, config: any, names: any}) => {
  return (
    <ParameterTable 
      classes={props.classes} 
      config={props.config}
      names={props.names}
      />
  );
}

const AlignmentRunning = (props: {config: any}) => {
  return (
    <LogDisplay jobId={props.config.job_id} parameter="test"/>
  );
}



const MainStepper = (props: {}) => {
  const classes = useStyles();
  // Handling steps
  const [activeStep, setActiveStep] = useState(0);
  const steps = ['Getting started', 'Inputs and outputs', 'Is everything ok?', 'Running']
  
  const handleNext = () => {
      if (activeStep == 1){
        const date = new Date();
        configDispatch({type: "job_id", value: date.getTime()});
      } 
      if (activeStep == 2){
        postConfig("alignment", configState)
      }
      setActiveStep((prevActiveStep) => prevActiveStep + 1);  
  };

  const handleBack = () => {
      setActiveStep((prevActiveStep) => prevActiveStep - 1);
  };
  
  const handleReset = () => {
      setActiveStep(3);
  };

  // Handling config
  const initialConfig = {
    job_id: "",
    input_dir: "",
    output_dir: "",
    channels: [],
    alignment_channel: ""
  };

  const configNames = {
    job_id: "Job ID",
    input_dir: "Input directory",
    output_dir: "Output directory",
    channels: "Channels",
    alignment_channel: "Alignment channel"

  }
  const [configState, configDispatch] = useReducer(configReducer, initialConfig);
  console.log(configState);

  // Stepper logic
  let stepperContent;
    switch (activeStep){
      case 0:
        stepperContent = <AlignmentGetStarted/>
        break;
      
      case 1:
        stepperContent = <AlignmentInputs 
                            classes={classes} 
                            config={configState}
                            onConfigChange={configDispatch}
                          />;
        break;

      case 2:
        stepperContent = <AlignmentConfirmation
                            classes={classes}
                            config={configState}
                            names={configNames}
                            />;
        break;
      
      case 3:
        stepperContent = <AlignmentRunning
                            config={configState}
                            />;
        break;
      
      default: 
        stepperContent = <AlignmentGetStarted/>
    }

  return (
    <div className={classes.stepper}>
    <Stepper className={classes.stepper} activeStep={activeStep} alternativeLabel>
        {steps.map((label) => (
        <Step key={label}>
            <StepLabel>{label}</StepLabel>
        </Step>
        ))}
    </Stepper>
    <div className={classes.stepper} >
        {activeStep === steps.length -1 ? (
        <div className={classes.stepper} >
            <div className={classes.stepperContent}>
            {stepperContent}
            </div>
            <Button onClick={handleReset}>Run another?</Button>
        </div>
        ) : (
        <div className={classes.stepper}>
            <div className={classes.stepperContent}>
            {stepperContent}
            </div>
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

export const Alignment =  (props: any) => {
  const styles = useStyles();


  return (
    <TopContent>
     
      <MainStepper/>
      
    </TopContent>
  );
};