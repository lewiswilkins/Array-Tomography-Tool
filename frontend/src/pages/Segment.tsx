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
import fetch from 'isomorphic-fetch';
import { stringify } from 'query-string';
import Iframe from 'react-iframe';
import {configReducer} from '../hooks/configReducer';
import { TextInput, NumericalInput } from '../components/Inputs';
import { ParameterTable } from '../components/ParameterTable';

const useStyles = makeStyles(theme => ({
  root: {
    // textAlign: "center",
    flexGrow: 1,
    // display: 'flex',
  },
  stepper: {
    width: '100%',
  },
  previsualiser: {
    flexGrow: 1
  },
  text: {
    textAlign: "left",
  },
  inputs: {
    '& .MuiTextField-root': {
        margin: theme.spacing(2),
        width: '25ch'}
  },
  backButton: {
    marginRight: theme.spacing(1),
  },
  formControl: {
    margin: theme.spacing(2),
    minWidth: 300,
    maxWidth: 800,
  },
  table: {
    minWidth: 200,
    // maxWidth: 400,
  },
  stepperContent: {
    padding: theme.spacing(2)
  }
}));

const thresholdParameterTemplate = {
  autolocal: {
    cFactor: 0,
    windowSize: 0
  },
  fixed: {
    threshold: 0
  },
};

const getBokeh = async (bokehName: string, fileName: string) => {
  const log = await fetch(
    `http://127.0.0.1:5000/segment/gui/${bokehName}/?${stringify({"fileName": fileName})}/`, {
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

const getFileList = async (directory: string) => {
  const params = {"directory": directory};
  const data =  await fetch(
    `http://127.0.0.1:5000/segment/list_files/?${stringify(params)}/`, {
      method: 'GET',
      mode: 'cors', 
      cache: 'no-cache',
      headers: {
          'Access-Control-Allow-Origin':'',
      },
  });

  const fileList = await data.json();
  console.log(fileList);
  return fileList.file_list;
}

const getThresholdMethodList = async () => {
  const data =  await fetch(
    `http://127.0.0.1:5000/segment/list_threshold_methods/`, {
      method: 'GET',
      mode: 'cors', 
      cache: 'no-cache',
      headers: {
          'Access-Control-Allow-Origin':'',
      },
  });

  const thresholdMethods = await data.json();
  console.log(thresholdMethods)
  return thresholdMethods.threshold_methods;
}

const Dropdown = (props: any) => {
  const id = `${props.id}-input`;
  const labelId = `${props.id}-label`;
  const selectId = `${props.id}-select`;

  return(
    
      <FormControl  className={props.classes.formControl}>
        <InputLabel id={id}>{props.text}</InputLabel>
        <Select
          // className={props.classes.inputs}
          labelId={labelId}
          id={selectId}
          value={props.value}
          onChange={props.handleChange}
        >
          {props.list.map((item: any, index: any) => (
            <MenuItem key={index} value={item}>{item}</MenuItem>
          ))}
        </Select>
      </FormControl>
    
  );
}

const PreVisualiser = (props: {thresholdMethod: string}) => {
  const src = `http://localhost:5006/segment_${props.thresholdMethod}_bokeh`
  console.log(src);
  return (
    <div>
      <Iframe id='bokeh_iframe' url={src} width='770' height='650' frameBorder={0} />
    </div>
  );
}

const PreVisualiserWindow = (props: {directory: string}) => {
  const classes = useStyles();

  const [fileList, setFileList] = useState([]);
  useEffect(() => {
    getFileList(props.directory).then(setFileList);
  }, []);

  const [file, setFile] = useState("");
  const handleFileChange = (event: React.ChangeEvent<{ value: unknown }>) => {
    setFile(event.target.value as string);
  }

  const [thresholdMethodList, setThresholdMethodList] = useState([]);
  useEffect(() => {
    getThresholdMethodList().then(setThresholdMethodList);
  }, []);

  const [thresholdMethod, setThresholdMethod] = useState("");
  const handleThresholdMethodChange = (event: React.ChangeEvent<{ value: unknown}>) => {
    setThresholdMethod(event.target.value as string);
  }
  
  const [loadPreVisualiser, setLoadPrevisualiser] = useState(false);

  const loadFunction = () => {
    getBokeh(thresholdMethod, file);
    setLoadPrevisualiser(true);
    wait(2500);
    refreshIFrame();
  }

  const wait = (ms: number) => {
    var d = new Date().getTime();
    var d2 = null;
    do { d2 = new Date().getTime(); }
    while(d2-d < ms);
  }

  const refreshIFrame = () => {
    var iframe: HTMLIFrameElement = document.getElementById('bokeh_iframe') as HTMLIFrameElement;
    if(iframe){
      console.log("refreshing")
      iframe.src = iframe.src;
    }
  }

  let previsualiser;
  loadPreVisualiser ? previsualiser = <PreVisualiser thresholdMethod={thresholdMethod}/> : previsualiser = <div/>;
    
  
 
  return(
    <div>
    <div className={classes.root}>
      <Grid 
        container 
        direction="row"
        justify="space-between"
        alignItems="center"
        // spacing={3}
      >
        <Grid item xs>
          <Dropdown 
            id="file"
            text="File"
            value={file}
            list={fileList}
            handleChange={handleFileChange}
            classes={classes}
          />
        </Grid>
        <Grid item xs>
          <Dropdown
            id="threshold"
            text="Threshold Method"
            value={thresholdMethod}
            list={thresholdMethodList}
            handleChange={handleThresholdMethodChange}
            classes={classes}
          />
        </Grid>
        <Grid item xs>
          <Button
            variant="contained"
            color="primary"
            onClick={loadFunction}
            // channelName={classes.inputs}
          >
            Load
          </Button>
        </Grid>

      </Grid>
      </div>
      <div className={classes.previsualiser}>
        {previsualiser}
      </div>
      </div>
        
        
    
  );
}

const SegmentGetStarted = (props: any) => {
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
                Welcome to the segment module! 🍰
            </Typography>
            <Typography 
              variant="h6">
                Here you will find all the wonderful things related to the module.
          </Typography>
      </Grid>
  );
}

const SegmentInputs = (props: {classes: any, config: {inputDir: string, outputDir: string}, onConfigChange: any}) => {
  return (
      <form className={props.classes.inputs} noValidate autoComplete="off">
            <TextInput
                label="Input directory"
                onChange={
                    (event: any) => {
                        console.log(event.target.value)
                        props.onConfigChange({
                            type: "inputDir", 
                            value: event.target.value
                            });
                    }
                }
                value={props.config.inputDir}
                classes={props.classes}
            />
            <TextInput
                label="Output directory"
                onChange={
                    (event: any) => {
                        console.log(event.target.value)
                        props.onConfigChange({
                            type: "outputDir", 
                            value: event.target.value
                            });
                    }
                }
                value={props.config.outputDir}
                classes={props.classes}
            />
        </form>
  );
}

const SegmentParameters = (props: {classes: any, config: any, configDispatch: any, parameters: any, parametersDispatch: any}) => {
  const [thresholdMethodList, setThresholdMethodList] = useState([]);
  useEffect(() => {
    getThresholdMethodList().then(setThresholdMethodList);
  }, []);

  let parameterPage;
  switch(props.config.thresholdMethod){
    case "autolocal":
      parameterPage = <SegmentAutolocalParameters 
                        classes={props.classes}
                        config={props.parameters}
                        onChange={props.parametersDispatch}
                        />;
      break;

    case "fixed": 
      parameterPage = <SegmentFixedParameters classes={props.classes}/>;
      break;

    default:
      parameterPage = <div></div>;
      break;
  }

  
  return (
    <div>
      <TextInput 
        classes={props.classes}
        label="Files"
        onChange={(event: any) => {
          console.log(event.target.value)
          props.configDispatch({
              type: "files", 
              value: event.target.value
              });}}
        value={props.config.files}
        />
      <Dropdown
        id="threshold"
        text="Threshold Method"
        value={props.config.thresholdMethod}
        list={thresholdMethodList}
        handleChange={(event: any) =>{
          props.configDispatch({type: "thresholdMethod", value: event.target.value })}
          }
        classes={props.classes}
      />
      {parameterPage}
    </div>
  );
}

const SegmentAutolocalParameters = (props: {classes: any, config: any, onChange: any}) => {

  return (
    <div>
      <NumericalInput 
        label="C-factor"
        classes={props.classes}
        onChange={(event: any) => props.onChange({type: "cFactor", value: event.target.value})}
        value={props.config.hasOwnProperty("cFactor") ?  props.config.cFactor : 0}
        inputProps={{step: 0.1,min: 0}}
        />
      <NumericalInput 
        label="Window size"
        classes={props.classes}
        onChange={(event: any) => props.onChange({type: "windowSize", value: event.target.value})}
        value={props.config.hasOwnProperty("windowSize") ?  props.config.windowSize : 0}
        inputProps={{step: 2,min: 1}}
        />
    </div>
  );
}


const SegmentFixedParameters = (props: {classes: any}) => {
  return (
    <div>
      {/* <NumericalInput 
        label="Threshold value"
        classes={props.classes}
        /> */}
   
    </div>
  );
}


const SegmentConfirmation = (props: {classes: any, config: any}) => {
  return (
    <ParameterTable classes={props.classes} config={props.config}/>
  );
}
const MainStepper = (props: {}) => {

  const classes = useStyles();
  // Handling steps
  const [activeStep, setActiveStep] = useState(0);
  const steps = ['Getting started', 'Inputs and outputs', 'Previsualiser', 'Segment parameters', 'Is everything ok?']
  
  const handleNext = () => {
      if (activeStep == 3){
        configDispatch({type: "thresholdParams", value: parameters})
      } 
      setActiveStep((prevActiveStep) => prevActiveStep + 1);  
  };

  const handleBack = () => {
      setActiveStep((prevActiveStep) => prevActiveStep - 1);
  };
  
  const handleReset = () => {
      setActiveStep(0);
  };

  // Handling config
  const initialConfig = {
    inputDir: "",
    outputDir: "",
    thresholdMethod: "",
    files: "",
    thresholdParams: {},
  };
  const [configState, configDispatch] = useReducer(configReducer, initialConfig);
  console.log(configState);

  // Handling params
  const initialParameters = {};
  const [parameters,  parameterDispatch] = useReducer(configReducer, initialParameters);
  // TODO: here need similar logic to the channels in the colocalisation - then
  // on clicking next it can set the params 

  // Stepper logic
  let stepperContent;
    switch (activeStep){
      case 0:
        stepperContent = <SegmentGetStarted/>
        break;
      
      case 1:
        stepperContent = <SegmentInputs 
                            classes={classes} 
                            config={configState}
                            onConfigChange={configDispatch}
                          />;
        break;

      case 2: 
        stepperContent = <PreVisualiserWindow 
                            directory={configState.inputDir}
                          />;
        break;
      
      case 3:
        stepperContent = <SegmentParameters
                            classes={classes}
                            config={configState}
                            configDispatch={configDispatch}
                            parameters={parameters}
                            parametersDispatch={parameterDispatch}
                          />;
        break;

      case 4:
        stepperContent = <SegmentConfirmation 
                            classes={classes}
                            config={configState}
                          />;
        break;

      default: 
        stepperContent = <SegmentGetStarted/>
    }

  return (
    <div className={classes.stepper}>
    <Stepper activeStep={activeStep} alternativeLabel>
        {steps.map((label) => (
        <Step key={label}>
            <StepLabel>{label}</StepLabel>
        </Step>
        ))}
    </Stepper>
    <div >
        {activeStep === steps.length ? (
        <div>
            <div className={classes.stepperContent}>
            {stepperContent}
            </div>
            <Button onClick={handleReset}>Reset</Button>
        </div>
        ) : (
        <div>
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

export const Segment =  (props: any) => {
  const styles = useStyles();
  const [bokeh, setData] = React.useState({url: "", script_id: ""});

  return (
    <TopContent>
     
      <MainStepper/>
      
    </TopContent>
  );
};