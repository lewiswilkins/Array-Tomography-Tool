# Array Tomography Tool
![Docker Cloud Build Status](https://img.shields.io/docker/cloud/build/lewiswilkins/array_tomography_tool)
## Running Array Tomography Tool 

The easiest method to running the tool is to use Docker. First you will require
Docker installed on your computer - go to
https://www.docker.com/products/docker-desktop to download and install. There
are now two versions of the tool available. One which runs from the command line
and the other now has a full browser based GUI. The instructions to run both are
below

### Running the GUI

First, the Docker image for the tool needs to be pulled. Go to your terminal and
paste in the following command


`docker pull lewiswilkins/array_tomography_tool:v1.0.0-alpha`

This will take a few mins to download, the image is around 1GB (hope to slim this down in
the future). Once downloaded run the following command:

`docker run -it -d -v /path/to/files/:/mnt/files/:delegated -p 3000:3000 -p
5000:5000 -p 5006:5006 lewiswilkins/array_tomography_tool:v1.0.0-alpha`

Here, you will need to replace `/path/to/files/` with the path to wherever your
files are.
Then, open your web browser (this is tested in Safari and Chrome so far) and
navigate to `localhost:3000`. This may take a few seconds to load while the
services are getting up and running in the Docker container. You should then see
the welcome screen! 

![Home page](images/home.png?raw=true "Home page")

Instructions on how to each module will be included on their respective pages.
For now it should all be fairly self explanatory. One thing to bear in mind -
when prompted for a path to an input or output directory, always prefix your
path with `/mnt/files/`. So, for example, if you wanted to navigate to a file
called `yourFile.txt` which is in `yourDir`, the full path would be
`/mnt/files/yourDir/yourFile.txt`.

#### Segmentation visualiser
![Segmentation visualiser](images/segment_visualiser.png?raw=true "Segmentation visualiser")

#### Colocalisation
![Colocalisation](images/coloc.png?raw=true "Colocalisation")


### Running from the command line

First, the Docker image for the tool needs to be pulled. Go to your terminal and
paste in the following command:


`docker pull lewiswilkins/array_tomography_tool:v0.2.5`


This will probably take a couple of mins to download. Once complete, you are
ready to run the tool. For now it only does the colocalisation. The tool takes 3
arguments:
- `--input` the directory with the input files 
- `--output` the output directory
- `--config` the `.yaml` config file containing the colocalisation parameters

An example of the config file can be found in this repo - `example_config.yaml`.
To run the tool, you will use the following command:


`docker run -it -v /path/to/files/:/mnt/files/:delegated lewiswilkins/array_tomography_tool:v0.2.5  --input
/mnt/files/inputs/ --output /mnt/files/output/ --config /mnt/files/config.yaml`

Here you will need to replace `/path/to/files/` with the path to wherever your
input files are. The suggested setup is to have a folder with two folders in it.
One called `inputs` which will contain all of the input images you wish to run
over. Another called `output` which will store the output images and numbers.
You should also put your config file in this directory.


