export const configReducer = (state: any, action: {type: string, value: any}) => {
    console.log(state);
    if (action.value == "RESET"){
        return {};
    } 
    else{
        return {...state, [action.type]: action.value};
    } 
};


export const channelsReducer = (state: any, action: {channel: string, coloc: string,  value: any}) => {
    if(action.channel === "init"){
        return action.value;
    }
    else {
        state[action.channel][action.coloc] = action.value;
        return {...state, [action.channel]:
            {...state[action.channel], [action.coloc]: action.value}
        };
    }
};