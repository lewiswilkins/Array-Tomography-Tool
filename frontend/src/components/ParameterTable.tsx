import React from "react";
import {
    Paper,
    TableContainer,
    Table,
    TableHead,
    TableRow,
    TableCell,
    TableBody,
    Typography,
  } from "@material-ui/core";


export const ParameterTable = (props: {classes: any,  config: any}) => {
    const flatConfig = flattenConfig(props.config)
    return (
        <TableContainer component={Paper}>
            <Table className={props.classes.table} >
                <TableHead>
                    <TableRow>
                        <TableCell><Typography style={{fontWeight: "bold"}}> Parameter </Typography></TableCell>
                        <TableCell><Typography style={{fontWeight: "bold"}}> Value </Typography></TableCell>
                    </TableRow>
                </TableHead>
                <TableBody>
                    {Object.keys(flatConfig).map((key: string) => (
                        <TableRow>
                        <TableCell component="th" scope="row">{key}</TableCell>
                        <TableCell>{flatConfig[key]}</TableCell>
                        </TableRow>
                    ))}
                </TableBody>
            </Table>
        </TableContainer>
    );
}


const flattenConfig = (config: any) => {
    const flatConfig = {} as any;
    for(const [key, value] of Object.entries(config)){
        if (typeof value === "object"){
            const innerConfig = flattenConfig(value);
            Object.assign(flatConfig, innerConfig);
        }
        else {
            flatConfig[key] = value;
        }
    }
    return flatConfig;
}