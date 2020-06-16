
export const postConfig = (endpoint: string, configState: any) => {
    return fetch(`http://127.0.0.1:5000/${endpoint}/`, {
    method: 'POST',
    body: JSON.stringify(configState),
    headers: {
        'Content-Type': 'application/json'
        },
    });
}

export const getLog = async (jobId: string, parameter: string) =>{
    const log = await fetch(
        `http://127.0.0.1:5000/colocalisation/${jobId}/${parameter}/`, {
        method: 'GET',
        mode: 'cors', 
        cache: 'no-cache',
        headers: {
            'Access-Control-Allow-Origin':'',
        },
    });
    const data = await log.text();
    console.log(data);

    return data;
}