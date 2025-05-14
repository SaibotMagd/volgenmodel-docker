import os
from os import listdir
from os.path import join, isfile
import tifffile
import SimpleITK as sitk
import numpy as np
import nibabel as nib
import numpy as np
from itertools import combinations
from datetime import datetime

def fileList(folder):
    from os import listdir
    from os.path import isfile, join
    fileListing = [f for f in listdir(folder) if isfile(join(folder, f))]
    fileListing.sort()
    return fileListing    

def create_N4_img(inputImagePath, outputPath):
    inputImage = sitk.ReadImage(inputImagePath)

    print("N4 bias correction runs.")
    maskImage = sitk.OtsuThreshold(inputImage,0,1,200)
    inputImage = sitk.Cast(inputImage,sitk.sitkFloat32)
    corrector = sitk.N4BiasFieldCorrectionImageFilter();
    output = corrector.Execute(inputImage,maskImage)
    sitk.WriteImage(output,outputPath)
    print("Finished N4 Bias Field Correction.....")

def get_threshold(image_array):
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

def create_cropped_imgs(input_folder,
                       output_folder,
                       thresholds='auto',
                       save_as_dtype=np.int16):
    for k, imageFile in enumerate(fileList(input_folder)):

        print(f"Processing image: {imageFile}")

        img = nib.load(join(input_folder, imageFile))
        img = img.get_fdata(dtype=np.float32)
        print(f"Initial Dims: {img.shape}")
        img = np.squeeze(img)        
        threshold = thresholds[k]
        """
        if thresholds != 'auto':
            try:
                threshold = thresholds[k]
            except:
                print(f"no threshold defined for this image: {imageFile}")
                return 1
        else:
            threshold = get_threshold(img)
            print(f"the auto created threshold == {threshold}")
            if threshold is None:
                print("I tried to get a threshold automatically but it failed, because not at least 20% of all values in the image are zeros.")
                return 1
        """
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
            continue

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
        nib.save(finalImage, join(output_folder, imageFile[:-4] + "_auto-crop.nii"))
        print(f"I saved to {join(output_folder, imageFile[:-4] + '_auto-crop.nii')}")

    return 0


def create_padding_imgs(input_folder, init_paddingSize='10%'):
    imageFiles = fileList(input_folder)
    for imageFile in imageFiles:
        print(imageFile)
        img = nib.load(join(input_folder, imageFile))
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
        nib.save(img, join(input_folder, imageFile[:-4] + "_padded.nii")) 
        print(f"I padded file: {imageFile} size of {paddingSize} in all 3D!")  

def nii_to_minc(inputFolder, outputFolder, only_preprocessed=1):
    def fileList(folder):
        from os import listdir
        from os.path import isfile, join
        fileListing = [f for f in listdir(folder) 
               if isfile(join(folder, f))]
        fileListing.sort()
        return fileListing    
      
    ## refresh niftiheader; step only neccessariy to prevent bugs in volgen-pipeline
    import nibabel as nib
    import numpy as np
    import os
    main_path = inputFolder
    out_folder = outputFolder
    main_files = fileList(main_path)

    if only_preprocessed:
        main_files = [x for x in main_files if x.find("N4") != -1 and x.find("padded") != -1 and x.find("auto-crop") != -1]
    
    for i, file in enumerate(main_files):
        n1_img = nib.load(join(main_path, file))
        n1_img.header.set_sform(np.diag([1, 1, 1, 1]), code='unknown')
        n1_img.header['dim'][0] = int(3)
        n1_img.header['extents'] = 0
        n1_img.header['sform_code'] = 1
        nib.save(n1_img, join(*[out_folder,'mouse' + str(i) + ".nii"]))
  
  ## convert from nii to minc, because volgenmodel can only use mnc files
    
    mainFiles = fileList(out_folder)
    for file in mainFiles:
        #print(file)
        if file.find('mouse') != -1 and file.find('nii') != -1:
            cmd = " ".join(['nii2mnc',
                '-unsigned',
                '-float',
                '-clobber',
                os.path.join(out_folder, file[:-4]),
                os.path.join(out_folder, file[:-4] + ".mnc")])
            print(cmd)    
            ## followed command could be used to use 32bit float files after 
            ## image normalization (i.e. to cut out parts in source image datasets)
            #os.system('nii2mnc -unsigned -float -clobber ' + out_folder + file[:-4] +
            #' ' + out_folder + file[:-4] + '.mnc')           
            os.system(cmd) 
  
  ## refresh mnc-header; step only neccessariy to prevent bugs in volgen-pipeline
    mainFiles = fileList(out_folder) 
    for file in mainFiles:
        #print(file)
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
  

def delete_files(folder, not_ending):
    files = os.listdir(folder)
    for file in files:
        if file[-3:] != not_ending:
            os.system(f"rm {os.path.join(folder,file)}")



def process_files(process_folder, output_folder, tmp_folder, create_parameters={'fit_stages': 'lin,1,2', 'ncpus': 8}, result_folder = '/volgenmodel-nipype'):
    # Get all .mnc files in the folder
    files = [f for f in os.listdir(process_folder) if f.endswith('.mnc')]

    # Sort files to ensure order consistency
    files.sort()

    # Iterate over all combination sizes (from 2 to len(files))
    for r in range(2, len(files) + 1): 
        # Jule: parameter zum aendern - hier die range(X aendern) 2 = "Anzahl der Kombinationspartner"
        # Achtung! X muss <= Anzahl der Bilder 
        # (d.h. der Wert darf maximal sogroß sein wie die Anzahl der bilder im Import_folder)
        for combo in combinations(files, r):
            # Create the output file name
            file_ids = [f.replace("mouse_", "").replace(".mnc", "") for f in combo]
            outputfile = f"TPL_{'_'.join(file_ids)}.nii"            
            combo_filelist = [os.path.join(process_folder, f) for f in list(combo)]
            print(combo_filelist)
            # Call the create_template function with the current combination
            create_template(combo_filelist, tmp_folder, create_parameters)
            # convert the template created for this combination
            convert_and_copy_mnc2nii(result_folder, outputfile)
            print(os.system(f"ls {output_folder}"))
    return 0

def create_template(filelist, tmp_folder, create_parameters, result_folder = '/volgenmodel-nipype'):
    tmp_files = os.listdir(tmp_folder)
    if len(tmp_files) > 0:
        print("there's an issue with the tmp folder, it isnt empty!")
        return 1
    else:
        # copy the current set of files that should be used to calculate the template to the tmp folder
        for file in filelist:
            print(f'cp {file} {tmp_folder}')
            os.system(f'cp {file} {tmp_folder}')
        # create the templates
        run_volgenmodel(tmp_folder, create_parameters)
        # clear the tmp-folder for the next template combination
        os.system(f'rm {tmp_folder}/*')
        return 0

## fit_stages siehe paper https://pubmed.ncbi.nlm.nih.gov/25620005/ , 
## entspricht der anzahl der registrierungsschritte 
## (d.h. mehr Schritte tendenziell bessere Qualität aber deutlich teurer)  

from IPython.display import display, HTML
import os

def run_volgenmodel(tmp_folder, create_parameters):
    cmd = " ".join(['python3',
                    '/volgenmodel-nipype/volgenmodel.py',
                    '--run=MultiProc',
                    f'--ncpus={create_parameters["ncpus"]}',
                    f'--fit_stages={create_parameters["fit_stages"]}',
                    f'--input_dir={tmp_folder}'])

    os.system(cmd)

def get_last_modified_subfolder(folder_path):
    last_modified_time = None
    last_modified_subfolder = None

    for root, dirs, files in os.walk(folder_path):
        for dir_name in dirs:
            dir_path = os.path.join(root, dir_name)
            # Get the most recent modification time in the folder (including its files and subfolders)
            for sub_root, _, sub_files in os.walk(dir_path):
                for file_name in sub_files:
                    file_path = os.path.join(sub_root, file_name)
                    file_mod_time = os.path.getmtime(file_path)
                    if last_modified_time is None or file_mod_time > last_modified_time:
                        last_modified_time = file_mod_time
                        last_modified_subfolder = dir_path

    if last_modified_subfolder:
        return last_modified_subfolder, datetime.fromtimestamp(last_modified_time).strftime('%Y-%m-%d %H:%M:%S')
    else:
        return None, None

def convert_and_copy_mnc2nii(folder_to_scan, output_filename, output_folder="/home/data/output_templates"):
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
        output_files = [f for f in os.listdir(os.path.join(subfolder,"model")) if os.path.isfile(os.path.join(os.path.join(subfolder,"model"), f))]
        if not output_files:
            print(f"There's no output folder with files: {subfolder}, {os.listdir(os.path.join(subfolder,'model'))}")
            return 1  # Return if the folder exists but is empty
    else:
        print(f"No valid output folder found: {subfolder}")
        return 1  # Return if the folder does not exist

    # Convert every result in the output folder to .nii, even if there are multiple outputs
    cwd = join(subfolder, 'model')
    input_files = [os.path.join(cwd, f) for f in os.listdir(cwd) if os.path.isfile(os.path.join(cwd, f))]
    for i, input_file in enumerate(input_files):
        if i != 0:
            output_file = os.path.join(output_folder,"_".join([str(i), output_filename]))
        else:
            output_file = os.path.join(output_folder,output_filename)
        cmd = " ".join(["mnc2nii", input_file, output_file])
        os.system(cmd)

    os.system(f"ls {output_folder}")

def delete_workflow_temp(search_folder="/volgenmodel-nipype/"):
    all_path_stuff = os.listdir(search_folder)
    for path in all_path_stuff:
        if path.startswith("workflow_temp"):
            print(path)
            cmd = ['rm', '-rf', join(search_folder, path)]
            os.system(cmd)