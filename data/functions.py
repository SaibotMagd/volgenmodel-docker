import os
from os import listdir
from os.path import join, isfile
import tifffile
import SimpleITK as sitk
import numpy as np
import nibabel as nib
from itertools import combinations
from datetime import datetime

def fileList(folder):
    """
    Generate a sorted list of files in the specified folder.

    Parameters:
    folder (str): Path to the directory whose files are to be listed.

    Returns:
    list: A sorted list of filenames in the specified folder.
    """
    fileListing = [f for f in listdir(folder) if isfile(join(folder, f))]
    fileListing.sort()
    return fileListing

def create_N4_img(inputImagePath, outputImagePath):
    """
    Perform N4 bias correction on an image and save the corrected image.

    This function reads an image from the input path, applies N4 bias field correction,
    and writes the corrected image to the output path.

    Parameters:
    inputImagePath (str): Path to the input image file.
    outputPath (str): Path where the corrected image will be saved.
    """
    inputImage = sitk.ReadImage(inputImagePath)

    print("N4 bias correction runs.")
    maskImage = sitk.OtsuThreshold(inputImage, 0, 1, 200)
    inputImage = sitk.Cast(inputImage, sitk.sitkFloat32)
    corrector = sitk.N4BiasFieldCorrectionImageFilter()
    output = corrector.Execute(inputImage, maskImage)
    sitk.WriteImage(output, outputImagePath)
    print(f"Finished N4 Bias Field Correction to {outputImagePath}")

def get_threshold(image_array):
    """
    Determine the threshold value for an image array based on the presence of zeros.

    This function checks if at least 20% of the values in the array are zeros.
    If so, it returns the lowest non-zero value in the array. Otherwise, it returns None.

    Parameters:
    image_array (numpy.ndarray): Input array representing the image.

    Returns:
    float or None: The lowest non-zero value if the condition is met, otherwise None.
    """
    # Flatten the array to simplify analysis
    flat_array = image_array.flatten()

    # Count the number of zeros
    num_zeros = np.count_nonzero(flat_array == 0)
    total_values = flat_array.size

    # Check if at least 20% of values are zeros
    if num_zeros / total_values >= 0.2:
        # Extract nonzero values
        nonzero_values = flat_array[flat_array != 0]

        # Return the lowest nonzero value if any exist
        if nonzero_values.size > 0:
            return np.min(nonzero_values)

    return None  # Return None if the condition isn't met

def create_cropped_imgs(inputImagePath, outputImagePath, threshold='auto', save_as_dtype=np.int16):
    """
    Create cropped images from input images based on specified or automatically determined thresholds.

    This function processes each image in the input folder, applies a threshold to determine
    the region of interest, crops the image accordingly, and saves the cropped image to the output folder.

    Parameters:
    inputImagePath (str): path to a skull stripped image file in nii format
    outputImagePath (str): Path to the folder where cropped image will be saved.
    threshold (str): Threshold value for the skull stripped image. If 'auto', threshold will determined automatically.
    save_as_dtype (data-type): Data type to save the cropped image as.

    Returns:
    int: 0 if successful, 1 if an error occurs.
    """

    print(f"Processing image: {inputImagePath}")

    img = nib.load(inputImagePath)
    #img = img.get_fdata(dtype=np.float32)
    img = img.get_fdata()
    print(f"Initial Dims: {img.shape}")
    img = np.squeeze(img)
    print(np.mean(img))
    if np.mean(img) < 1:
        img = img * 1000

    if threshold != 'auto':
        try:
            print(f"current threshold is {threshold}")
        except:
            print(f"No threshold defined for this image: {inputImagePath}")
            return 1
    else:
        threshold = get_threshold(img)
        print(f"The auto-created threshold == {threshold}")
        if threshold is None:
            print("I tried to get a threshold automatically but it failed, because not at least 20% of all values in the image are zeros.")
            return 1

    zLen = img.shape[0]
    bestBorders = [int(img.shape[1]/2)-1, int(img.shape[1]/2)+1,
                 int(img.shape[2]/2)-1, int(img.shape[2]/2)+1]

    print(f"Initial bestBorders: {bestBorders}")

    for i in range(np.size(img, axis=0)):
        image_data = img[i]
        if np.max(image_data) <= threshold:
            zLen -= 1
            continue

        non_empty_columns = np.where(np.max(image_data, axis=0) > threshold)[0]
        non_empty_rows = np.where(np.max(image_data, axis=1) > threshold)[0]
        cropBox = [min(non_empty_rows), max(non_empty_rows), min(non_empty_columns), max(non_empty_columns)]

        if i == 0:
            bestBorders = cropBox
        else:
            for pos, cropCheck in enumerate(cropBox):
                if (pos == 0 or pos == 2) and bestBorders[pos] > cropCheck:
                    bestBorders[pos] = cropCheck
                if (pos == 1 or pos == 3) and bestBorders[pos] < cropCheck:
                    bestBorders[pos] = cropCheck

    print(f"Final bestBorders: {bestBorders}")

    # Check if bestBorders are valid
    if bestBorders[0] >= bestBorders[1] or bestBorders[2] >= bestBorders[3]:
        print("Invalid crop borders detected. Skipping this image.")
        return 1

    image_data_new = image_data[bestBorders[0]:bestBorders[1]+1, bestBorders[2]:bestBorders[3]+1]
    finalImage = np.zeros((zLen, image_data_new.shape[0], image_data_new.shape[1]), dtype=save_as_dtype)
    iCount = 0

    print(f"Number of slices after: {np.size(finalImage, axis=0)}")
    print(f"Final Dims: {finalImage.shape}")

    for i in range(np.size(img, axis=0)):
        image_data = img[i]
        if np.max(image_data) <= threshold:
            continue
        finalImage[iCount] = image_data[bestBorders[0]:bestBorders[1]+1, bestBorders[2]:bestBorders[3]+1]
        iCount += 1
        if iCount == zLen:
            break

    finalImage = nib.Nifti1Image(finalImage, np.eye(4))
    nib.save(finalImage, outputImagePath)
    print(f"I saved to {outputImagePath}")

    return 0

def create_padding_imgs(inputImagePath, outputImagePath, init_paddingSize='10%'):
    """
    Create padded images by adding padding around the input images.

    This function processes each image in the input folder, adds padding around the image,
    and saves the padded image back to the input folder.

    Parameters:
    inputImagePath (str): imput path for the preprocessed mri image file.
    outputImagePath (str): target path for the preprocessed mri image file.
    init_paddingSize (int or str): Size of the padding. If '10%', padding is 10% of the maximum image dimension.
    """
    print(inputImagePath)
    img = nib.load(inputImagePath)
    img = img.get_fdata(dtype=np.float32)
    img = np.squeeze(img)
    if init_paddingSize == '10%':
        paddingSize = int(max(img.shape)*0.1) + 1
    else:
        paddingSize = init_paddingSize
    img = np.pad(img, ((paddingSize,paddingSize),
                      (paddingSize,paddingSize),
                      (paddingSize,paddingSize)),
                'constant') #z-y-x
    img = nib.Nifti1Image(img, np.eye(4))
    nib.save(img, outputImagePath)
    print(f"I padded file: {outputImagePath} size of {paddingSize} in all 3D!")

def nii_to_minc(inputFolder, outputFolder, only_preprocessed=1):
    """
    Convert NIfTI images to MINC format and refresh headers to prevent bugs in the volgen pipeline.

    This function processes each NIfTI image in the input folder, refreshes the header,
    converts the image to MINC format, and saves it to the output folder.

    Parameters:
    inputFolder (str): Path to the folder containing input NIfTI images.
    outputFolder (str): Path to the folder where MINC images will be saved.
    only_preprocessed (bool): If True, only process preprocessed images.
    """

    ## Refresh NIfTI header; step only necessary to prevent bugs in volgen-pipeline
    main_path = inputFolder
    out_folder = outputFolder
    main_files = fileList(main_path)

    if only_preprocessed:
        main_files = [x for x in main_files if x.find("_N4_auto-crop_padded.") != -1]

    for i, file in enumerate(main_files):
        n1_img = nib.load(join(main_path, file))
        n1_img.header.set_sform(np.diag([1, 1, 1, 1]), code='unknown')
        n1_img.header['dim'][0] = int(3)
        n1_img.header['extents'] = 0
        n1_img.header['sform_code'] = 1
        nib.save(n1_img, join(*[out_folder,'mouse' + str(i) + ".nii"]))

    ## Convert from NIfTI to MINC, because volgenmodel can only use MNC files
    mainFiles = fileList(out_folder)
    for file in mainFiles:
        if file.find('mouse') != -1 and file.find('nii') != -1:
            cmd = " ".join(['nii2mnc',
                '-unsigned',
                '-float',
                '-clobber',
                os.path.join(out_folder, file[:-4] + ".nii"),
                os.path.join(out_folder, file[:-4] + ".mnc")])
            print(cmd)
            os.system(cmd)
    """
    ## Refresh MINC header; step only necessary to prevent bugs in volgen-pipeline
    mainFiles = fileList(out_folder)
    for file in mainFiles:
        if file[-3:] == 'mnc':
            os.system('mincreshape -clobber -2 +direction' +
                    ' -dimorder zspace,yspace,xspace' +
                    ' -dimsize xspace=-1' +
                    ' -dimsize yspace=-1' +
                    ' -dimsize zspace=-1' +
                    ' ' + os.path.join(*[out_folder, file]) + ' ' +
                    os.path.join(*[out_folder, file])
                   )
            print(f"{file} -> reworked_mouse_{file}")
    """
    
def delete_files(folder, not_ending):
    """
    Delete files in a folder that do not end with a specified extension.

    Parameters:
    folder (str): Path to the folder containing files to be processed.
    not_ending (str): File extension to exclude from deletion.
    """
    files = os.listdir(folder)
    for file in files:
        if file[-3:] != not_ending:
            os.system(f"rm {join(folder, file)}")

def process_files(process_folder, output_folder, tmp_folder, create_parameters={'fit_stages': 'lin,1,2', 'ncpus': 8}, result_folder='/volgenmodel-nipype'):
    """
    Process files in a folder to create templates and convert them to NIfTI format.

    This function processes all .mnc files in the input folder, creates templates for each combination of files,
    and converts the templates to NIfTI format.

    Parameters:
    process_folder (str): Path to the folder containing input .mnc files.
    output_folder (str): Path to the folder where output files will be saved.
    tmp_folder (str): Path to the temporary folder used for processing.
    create_parameters (dict): Parameters for creating templates.
    result_folder (str): Path to the folder where the volgenmodel results are stored.

    Returns:
    int: 0 if successful.
    """

    
    # Get all .mnc files in the folder
    files = [f for f in os.listdir(process_folder) if f.endswith('.mnc')]
    ## make sure that the template contains of every brain image given if no parameters set
    if not isinstance(create_parameters['min_number_of_brains_in_template'], int) or create_parameters['min_number_of_brains_in_template'] > len(files):
        create_parameters['min_number_of_brains_in_template'] = len(files)

    # Sort files to ensure order consistency
    files.sort()

    # Iterate over all combination sizes (from 2 to len(files))
    for r in range(create_parameters['min_number_of_brains_in_template'], len(files) + 1):
        for combo in combinations(files, r):
            # Create the output file name
            file_ids = [f.replace("mouse_", "").replace(".mnc", "") for f in combo]
            outputfile = f"TPL_{'_'.join(file_ids)}.nii"
            combo_filelist = [join(process_folder, f) for f in list(combo)]
            print(combo_filelist)
            # Call the create_template function with the current combination
            create_template(combo_filelist, tmp_folder, create_parameters)
            # Convert the template created for this combination
            convert_and_copy_mnc2nii(result_folder, outputfile)
            #print(os.system(f"ls {output_folder}"))
    return 0

def create_template(filelist, tmp_folder, create_parameters, result_folder='/volgenmodel-nipype'):
    """
    Create a template from a list of files and save it to the result folder.

    This function copies the input files to a temporary folder, creates a template using volgenmodel,
    and clears the temporary folder.

    Parameters:
    filelist (list): List of file paths to create the template from.
    tmp_folder (str): Path to the temporary folder used for processing.
    create_parameters (dict): Parameters for creating templates.
    result_folder (str): Path to the folder where the volgenmodel results are stored.

    Returns:
    int: 0 if successful, 1 if there is an issue with the temporary folder.
    """
    tmp_files = os.listdir(tmp_folder)
    if len(tmp_files) > 0:
        print("There's an issue with the tmp folder, it isn't empty!")
        return 1
    else:
        # Copy the current set of files that should be used to calculate the template to the tmp folder
        for file in filelist:
            print(f'cp {file} {tmp_folder}')
            os.system(f'cp {file} {tmp_folder}')
        # Create the templates
        run_volgenmodel(tmp_folder, create_parameters)
        # Clear the tmp-folder for the next template combination
        os.system(f'rm {tmp_folder}/*')
        return 0

def run_volgenmodel(tmp_folder, create_parameters):
    """
    Run the volgenmodel to create templates from files in the temporary folder.

    Parameters:
    tmp_folder (str): Path to the temporary folder containing files to process.
    create_parameters (dict): Parameters for creating templates.
    """
    cmd = " ".join(['python3',
                    '/volgenmodel-nipype/volgenmodel.py',
                    '--run=MultiProc',
                    f'--ncpus={create_parameters["ncpus"]}',
                    f'--fit_stages={create_parameters["fit_stages"]}',
                    f'--input_dir={tmp_folder}'])

    os.system(cmd)

def get_last_modified_subfolder(folder_path):
    """
    Get the last modified subfolder in a given folder path.

    Parameters:
    folder_path (str): Path to the folder to search for subfolders.

    Returns:
    tuple: Path to the last modified subfolder and its last modified time as a formatted string.
    """
    last_modified_time = None
    last_modified_subfolder = None

    for root, dirs, files in os.walk(folder_path):
        for dir_name in dirs:
            dir_path = join(root, dir_name)
            # Get the most recent modification time in the folder (including its files and subfolders)
            for sub_root, _, sub_files in os.walk(dir_path):
                for file_name in sub_files:
                    file_path = join(sub_root, file_name)
                    file_mod_time = os.path.getmtime(file_path)
                    if last_modified_time is None or file_mod_time > last_modified_time:
                        last_modified_time = file_mod_time
                        last_modified_subfolder = dir_path

    if last_modified_subfolder:
        return last_modified_subfolder, datetime.fromtimestamp(last_modified_time).strftime('%Y-%m-%d %H:%M:%S')
    else:
        return None, None

def convert_and_copy_mnc2nii(folder_to_scan, output_filename, output_folder="/home/data/output_templates"):
    """
    Convert and copy MINC files to NIfTI format from the last modified subfolder.

    This function identifies the last modified subfolder in the specified folder, checks for output files,
    and converts them to NIfTI format.

    Parameters:
    folder_to_scan (str): Path to the folder to scan for subfolders.
    output_filename (str): Name of the output file.
    output_folder (str): Path to the folder where the output files will be saved.

    Returns:
    int: 0 if successful, 1 if no valid subfolder or output files are found.
    """
    subfolder, mod_time = get_last_modified_subfolder(folder_to_scan)
    if subfolder:
        print(f"The last modified subfolder is: {subfolder}")
        print(f"Last modification time: {mod_time}")
    else:
        print("No subfolders found or no modifications detected.")
        return 1  # Return early if no subfolder is found

    # Change subfolder if its name contains "temp" to "output"
    subfolder = subfolder.replace("temp", "output")

    # Check if "output" subfolder exists and contains files
    if "output" in subfolder and os.path.exists(subfolder):
        output_files = [f for f in os.listdir(join(subfolder, "model")) if os.path.isfile(join(join(subfolder, "model"), f))]
        if not output_files:
            print(f"There's no output folder with files: {subfolder}, {os.listdir(join(subfolder, 'model'))}")
            return 1  # Return if the folder exists but is empty
    else:
        print(f"No valid output folder found: {subfolder}")
        return 1  # Return if the folder does not exist

    # Convert every result in the output folder to .nii, even if there are multiple outputs
    cwd = join(subfolder, 'model')
    input_files = [join(cwd, f) for f in os.listdir(cwd) if os.path.isfile(join(cwd, f))]
    for i, input_file in enumerate(input_files):
        if i != 0:
            output_file = join(output_folder, "_".join([str(i), output_filename]))
        else:
            output_file = join(output_folder, output_filename)
        cmd = " ".join(["mnc2nii", input_file, output_file])
        os.system(cmd)

    os.system(f"ls {output_folder}")

def delete_workflow_temp(search_folder="/volgenmodel-nipype/"):
    """
    Delete temporary workflow folders.

    This function searches for and deletes folders that start with "workflow_temp" in the specified search folder.

    Parameters:
    search_folder (str): Path to the folder to search for temporary workflow folders.
    """
    all_path_stuff = os.listdir(search_folder)
    for path in all_path_stuff:
        if path.startswith("workflow_temp"):
            print(path)
            cmd = ['rm', '-rf', join(search_folder, path)]
            os.system(" ".join(cmd))

