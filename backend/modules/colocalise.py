import logging
import time 
from lib import SegmentedFile, colocalisation, ColocalisationResult, segment



logger = logging.getLogger(__name__)

def process_stack(
    name: str,
    config: dict, 
    in_dir: str,
    out_dir: str
):
    if "job_id" in config:
        job_id = config["job_id"]
        fh = logging.FileHandler('spam.log')
    logger.info(f"Processing {name}")
    log(config, "case_name", name)
    channels = []
    for channel_filepath in get_channels(name, config["channels"], in_dir):
        channel_file = SegmentedFile.from_tiff(channel_filepath)
        channels.append(channel_file)

    colocalised_results = []
    t_colocalise_s = time.time()
    for channel_1  in channels:
        logger.info(f"Colocalising {channel_1.channel_name} with all other channels.")
        log(config, "colocalising", channel_1.channel_name)
        temp_colocalised_result = ColocalisationResult.from_channel_file(channel_1)
        for channel_2 in channels:
            if channel_1.channel_name == channel_2.channel_name:
                continue
            if config["channels"][channel_1.channel_name][channel_2.channel_name].lower() == "none":
                continue
            temp_colocalised_channel = channel_1.colocalise_with(channel_2, config)
            if temp_colocalised_channel is ValueError:
                logger.warning(f"There seems to be a mismatch of image dimensions. Check all \
                    the images in {name} have the same number of stacks. Skipping\
                    for now.")
                log(config, "colocalising", "Image dimension mismatch!")
                return None
            temp_colocalised_result.add_colocalised_image(temp_colocalised_channel)
        temp_colocalised_result.calculate_combination_images()
        colocalised_results.append(temp_colocalised_result)
    t_colocalise_e = time.time()
    logger.debug(f"Time for colocalise = {t_colocalise_e-t_colocalise_s}")
    t_output_s = time.time()
    output_results_csv(colocalised_results, out_dir, config["output_filename"])
    t_output_e = time.time()
    logger.debug(f"Time for output = {t_output_e-t_output_s}")

    t_save_s = time.time()
    for result in colocalised_results:
        result.save_images(out_dir)
    t_save_e = time.time()
    logger.debug(f"Time for save = {t_save_e-t_save_s}")



def output_results_csv(colocalised_results, out_dir, out_file_name):
    logger.info("Saving csv.")
    file_path = os.path.join(out_dir, out_file_name)
    if os.path.isfile(file_path):
        pd = read_csv(file_path)
        csv_dict = pd.to_dict("list")
    else:
        csv_dict = create_csv_dict(colocalised_results)
    for result in colocalised_results:
        csv_dict["name"].append(result.name)
        csv_dict["channel"].append(result.channel_name)
        csv_dict["objects"].append(len(result.original_coords))
        combination_object_count = {
            x.colocalised_with : len(x.object_list) for x in result.colocalised_images
            }
        for key in get_combination_names(colocalised_results):
            if key in combination_object_count:
                csv_dict[key].append(combination_object_count[key])
            else:
                csv_dict[key].append(0)
    csv_dataframe = DataFrame(csv_dict, columns=csv_dict.keys())
    csv_dataframe.to_csv(
        file_path,
        index=None,
        )

def create_csv_dict(colocalised_results):
    titles_dict = {"name" : [], "channel" : [], "objects" : []}
    combination_dict = {}
    for key in get_combination_names(colocalised_results):
        combination_dict[key] = []
    return {**titles_dict, **combination_dict}

def get_combination_names(colocalised_results):
    combination_names = set()
    for result in colocalised_results:
        combination_names.add(result.channel_name)
        for image in result.colocalised_images:
            combination_names.add(image.colocalised_with)
    return combination_names
                    
def get_names(dir_path):
    names = set()
    r = re.compile(r"^.*\/(.*)-.*.tif")
    for filename in glob.glob(f"{dir_path}/*.tif"):
        match = r.match(filename)
        name = match.group(1)
        names.add(name)

    return list(names)


def get_channels(name, channels, dir_path):
    channels = [f"{dir_path}/{name}-{channel}.tif" for channel in channels]
    return channels

