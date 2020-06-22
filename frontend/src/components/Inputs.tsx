import React from 'react';
import TextField  from '@material-ui/core/TextField';

export const TextInput = (props: {classes: any, label: string, onChange: any, value: string}) => {
    const id = `${props.label}-textinput`
    return(
        <TextField
            className={props.classes.inputs}
            id={id}
            label={props.label}
            variant="outlined"
            onChange={props.onChange}
            value={props.value}
        />
    );
}

export const NumericalInput = (props: {classes: any, label: string, onChange: any, inputProps: any, value: number}) => {
    const id = `${props.label}-numericalinput`
    return(
        <TextField  
            className={props.classes.inputs}
            id={id}
            label={props.label}
            type="number"
            onChange={props.onChange}
            inputProps={props.inputProps}
            variant="outlined"
            value={props.value}
        />
    );
}