
from subprocess import call
import os
import shutil
import nibabel as nib
import numpy as np

#Set the paths to Anima and TractSeg here
animaBinsPath = "path/to/Anima"
tractSegBinsPath = "path/to/Tractseg"
work_dir = "path/to/work_dir"
data_dir = "path/to/diff/dir"
trk_dir = 'path/to/segmented/tracts'
os.mkdir(work_dir)
os.chdir(work_dir)
#bundles = ['AF', 'CG', 'CST', 'OR', 'SLF_I', 'CC_1']
bundles = ['AF', 'CC_1']

#load subjects ids from sujets.txt file and store them in a list
subjects_file = open('subjects.txt', 'r') #there must not be any empty line below the last subject line in sujets.txt file
subjects = []
for line in subjects_file.readlines():
      subjects.append(line)
subjects_file.close()
subjects = [subject[:-1] for subject in subjects[:-1]] + [subjects[-1]] #to remove '\n'




def computeAIC(in_file, out_file):
      imgdata = nib.load(in_file)
      noise = np.asanyarray(imgdata.dataobj)
      aic = np.zeros(noise.shape)
      aicMax = 0
      aicMin = 1e9
      for i in range(0, noise.shape[0]):
            for j in range(0, noise.shape[1]):
                  for k in range(0, noise.shape[2]):
                        if (noise[i, j, k] != 0.):
                              val = 45*(np.log(noise[i, j, k]/45))
                              aic[i, j, k] = val
                              if(val) > aicMax:
                                    aicMax = val
                              if(val < aicMin):
                                    aicMin = val
                        else:
                              aic[i, j, k] = 0.
    
      for i in range(0, noise.shape[0]):
            for j in range(0, noise.shape[1]):
                  for k in range(0, noise.shape[2]):
                        aic[i, j, k] = (aic[i, j, k] - aicMin)/(aicMax - aicMin)

      resImg = nib.Nifti1Image(aic, imgdata.affine, imgdata.header)
      nib.save(resImg, out_file)


#for group in range(1,9):
for group in range(1,2):
      #separate between train and test subjects
      if group == 1:
            test_subjects = subjects[100:105]
            train_subjects = subjects[0:100]
      else:
            test_subjects = subjects[(group-2)*5:(group-2)*5+5]
            train_subjects = subjects[0:(group-2)*5]+subjects[(group-2)*5+5:]
      test_subjects = test_subjects[0:1]
      train_subjects = train_subjects[0:3]
    
      os.mkdir('group{}'.format(group))
      os.chdir('group{}'.format(group))



      #PRIOR COMPUTATION
            #Build Folders
      print("BUILDING FOLDERS...")
      shutil.copyfile('../../averageDTI8.nrrd'.format(group), 'averageDTI8.nrrd')
      os.mkdir('prior')
      os.chdir('prior')
      os.mkdir('Fibers')
      os.mkdir('TODs')

      shutil.copytree("../../Transformations".format(group), "Transfos")
      shutil.copytree("../../residualDir".format(group), "residualDir")
      os.chdir('Fibers')
      for bundle in bundles:
            os.mkdir('{}'.format(bundle))
      os.chdir('..')
      os.chdir('TODs')
      for bundle in bundles:
            os.mkdir('{}'.format(bundle))
      os.chdir('..')
    


            #Computations
      print("PRIOR COMPUTATIONS...")
      for bundle in bundles:
            print("BUNDLE {}...".format(bundle))
            tod = open("TODs/{}/tod.txt".format(bundle), "a")
            weightTOD = open("TODs/{}/weight.txt".format(bundle), "a")

            for i, subject in enumerate(train_subjects):
                  if bundle == 'CC_1':
                        #case of "single" bundles
                        call([animaBinsPath + "animaFibersApplyTransformSerie",
                              "-t", "Transfos/DTI_{}.xml".format(subject),
                              "-i", + trk_dir + "/{0}/Tracks/{1}_right.vtp".format(subject, bundle),
                              "-o", "Fibers/{0}/{0}_{1}.vtp".format(bundle, subject)])

                        call([animaBinsPath + "animaTODEstimator",
                              "-i", "Fibers/{0}/{0}_{1}.vtp".format(bundle, subject),
                              "-o", "TODs/{0}/{0}_{1}.nii.gz".format(bundle, subject),
                              "-g", "../averageDTI8.nrrd"])

                        call([animaBinsPath + "animaImageToMask",
                              "-i", "TODs/{0}/{0}_{1}.nii.gz".format(bundle, subject),
                              "-o", "TODs/{0}/Mask_{0}_{1}.nii.gz".format(bundle, subject)])

                        call([animaBinsPath + "animaCreateImage",
                              "-g", "TODs/{0}/Mask_{0}_{1}.nii.gz".format(bundle, subject),
                              "-o", "TODs/{0}/poids_{0}_{1}.nrrd".format(bundle, subject),
                              "-b", "1"])

                        if i<2:
                              tod.write("TODs/{0}/{0}_{1}.nii.gz\n".format(bundle, subject))
                              weightTOD.write("TODs/{0}/poids_{0}_{1}.nrrd\n".format(bundle, subject))
                        else:
                              #it's the last line so we don't write "\n" at the end of the line (otherwise animaODFAverage doesn't work)
                              tod.write("TODs/{0}/{0}_{1}.nii.gz".format(bundle, subject))
                              weightTOD.write("TODs/{0}/poids_{0}_{1}.nrrd".format(bundle, subject))

                  else:
                        #case of "double" bundles (with left and right parts)
                        call([animaBinsPath + "animaFibersApplyTransformSerie",
                              "-t", "Transfos/DTI_{}.xml".format(subject),
                              "-i", + trk_dir + "/{0}/Tracks/{1}_right.vtp".format(subject, bundle),
                              "-o", "Fibers/{0}/{0}l_{1}.vtp".format(bundle, subject)])
                        call([animaBinsPath + "animaFibersApplyTransformSerie",
                              "-t", "Transfos/DTI_{}.xml".format(subject),
                              "-i", + trk_dir + "/{0}/Tracks/{1}_right.vtp".format(subject, bundle),
                              "-o", "Fibers/{0}/{0}r_{1}.vtp".format(bundle, subject)])
                        

                        call([animaBinsPath + "animaTODEstimator",
                              "-i", "Fibers/{0}/{0}l_{1}.vtp".format(bundle, subject),
                              "-o", "TODs/{0}/{0}l_{1}.nii.gz".format(bundle, subject),
                              "-g", "../averageDTI8.nrrd"])
                        call([animaBinsPath + "animaTODEstimator",
                              "-i", "Fibers/{0}/{0}r_{1}.vtp".format(bundle, subject),
                              "-o", "TODs/{0}/{0}r_{1}.nii.gz".format(bundle, subject),
                              "-g", "../averageDTI8.nrrd"])


                        call([animaBinsPath + "animaImageToMask",
                              "-i", "TODs/{0}/{0}l_{1}.nii.gz".format(bundle, subject),
                              "-o", "TODs/{0}/Mask_{0}l_{1}.nii.gz".format(bundle, subject)])
                        call([animaBinsPath + "animaImageToMask",
                              "-i", "TODs/{0}/{0}r_{1}.nii.gz".format(bundle, subject),
                              "-o", "TODs/{0}/Mask_{0}r_{1}.nii.gz".format(bundle, subject)])


                        call([animaBinsPath + "animaCreateImage",
                              "-g", "TODs/{0}/Mask_{0}l_{1}.nii.gz".format(bundle, subject),
                              "-o", "TODs/{0}/poids_{0}l_{1}.nrrd".format(bundle, subject),
                              "-b", "1"])
                        call([animaBinsPath + "animaCreateImage",
                              "-g", "TODs/{0}/Mask_{0}r_{1}.nii.gz".format(bundle, subject),
                              "-o", "TODs/{0}/poids_{0}r_{1}.nrrd".format(bundle, subject),
                              "-b", "1"])

                        if i<2:
                              tod.write("TODs/{0}/{0}l_{1}.nii.gz\n".format(bundle, subject))
                              tod.write("TODs/{0}/{0}r_{1}.nii.gz\n".format(bundle, subject))
                              weightTOD.write("TODs/{0}/poids_{0}l_{1}.nrrd\n".format(bundle, subject))
                              weightTOD.write("TODs/{0}/poids_{0}r_{1}.nrrd\n".format(bundle, subject))
                        else:
                              tod.write("TODs/{0}/{0}l_{1}.nii.gz\n".format(bundle, subject))
                              tod.write("TODs/{0}/{0}r_{1}.nii.gz".format(bundle, subject))
                              weightTOD.write("TODs/{0}/poids_{0}l_{1}.nrrd\n".format(bundle, subject))
                              weightTOD.write("TODs/{0}/poids_{0}r_{1}.nrrd".format(bundle, subject))

            tod.close()
            weightTOD.close()

            call([animaBinsPath + "animaODFAverage",
                  "-i", "TODs/{}/tod.txt".format(bundle),
                  "-w", "TODs/{}/weight.txt".format(bundle),
                  "-o", "TODs/{0}/average_{0}.nii.gz".format(bundle)])
      
      os.chdir('..')


      #TEST SUBJECT COMPUTATION
      print("TEST SUBJECT COMPUTATION...")
      os.mkdir("test_subjects")
      os.chdir("test_subjects")

      for subject in test_subjects:
            print("SUBJECT {}".format(subject))
            os.mkdir("{}".format(subject))
            os.chdir("{}".format(subject))

            #The two following commands are not used for now, one can ignore them
            '''
            convertImageCommand = [animaBinsPath + "animaConvertImage", 
                                    "-i", + data_dir + "/{}/Images/data.nii.gz".format(subject),
                                    "-g", + data_dir + "/{}/Images/data.bvec".format(subject),
                                    "-o", "{}_trDWI.nii.gz".format(subject),
                                    "-R", "LAS"]
            call(convertImageCommand)
            

            tractSegCommand = ["TractSeg", "-i", "{}_trDWI.nii.gz".format(subject),
                              "--bvals", + data_dir + "/{}/Images/data.bval".format(subject),
                              "--bvec", "{}_trDWI.bvec".format(subject),
                              "--raw_diffusion_input",
                              "-o", "tractseg",
                              "--output_type", "tract_segmentation",
                              "--brain_mask", + data_dir + "/{}/Masks/nodif_brain_mask.nii.gz".format(subject)]
            call(tractSegCommand)  
            '''

            call([animaBinsPath + "animaDTIEstimator",
                  "-i", + data_dir + "/{}/Images/data.nii.gz".format(subject),
                  "-b", + data_dir + "/{}/Images/data.bval".format(subject),
                  "-g", + data_dir + "/{}/Images/data.bvec".format(subject),
                  "-o", "{}_DTI.nii.gz".format(subject)])

            call([animaBinsPath + "animaODFEstimator", "-k", "8", "-R",
                  "-i", + data_dir + "/{}/Images/data.nii.gz".format(subject),
                  "-b", + data_dir + "/{}/Images/data.bval".format(subject),
                  "-g", + data_dir + "/{}/Images/data.bvec".format(subject),
                  "-V", "{}_noise.nii.gz".format(subject),
                  "-o", "{}_ODF.nii.gz".format(subject)])
            
            call([animaBinsPath + "animaDenseTensorSVFBMRegistration",
                  "-m", "{}_DTI.nii.gz".format(subject),
                  "-r", "../../averageDTI8.nrrd",
                  "-o", "{}_DTI_template.nii.gz".format(subject),
                  "-O", "{}_DTI_DefField.nii.gz".format(subject)])
            
            call([animaBinsPath + "animaDTIScalarMaps",
                  "-i", "{}_DTI_template.nii.gz".format(subject),
                  "-f", "{}_DTI_template_FA.nii.gz".format(subject)])

            call([animaBinsPath + "animaTransformSerieXmlGenerator",
                  "-i", "{}_DTI_DefField.nii.gz".format(subject),
                  "-o", "{}_DTI_DefField.xml".format(subject)])

            call([animaBinsPath + "animaODFApplyTransformSerie",
                  "-i", "{}_ODF.nii.gz".format(subject),
                  "-t", "{}_DTI_DefField.xml".format(subject),
                  "-g", "{}_DTI_template_FA.nii.gz".format(subject),
                  "-o", "{}_ODF_template.nii.gz".format(subject)])
            
            call([animaBinsPath + "animaApplyTransformSerie",
                  "-i", "{}_noise.nii.gz".format(subject),
                  "-t", "{}_DTI_DefField.xml".format(subject),
                  "-g", "{}_DTI_template_FA.nii.gz".format(subject),
                  "-o", "{}_noise_template.nii.gz".format(subject)])
            
            computeAIC("{}_noise_template.nii.gz".format(subject), "{}_AIC.nii.gz".format(subject))

            call([animaBinsPath + "animaGeneralizedFA", "-i", "{}_ODF_template.nii.gz".format(subject),
                  "-o", "{}_GFA.nii.gz".format(subject)])

            call([animaBinsPath + "animaImageArithmetic", "-i", "{}_AIC.nii.gz".format(subject),
                  "-M", "0.35", "-o", "{}_tmpAIC.nii.gz".format(subject)])
            
            call([animaBinsPath + "animaImageArithmetic", "-i", "{}_GFA.nii.gz".format(subject),
                  "-M", "0.65", "-o", "{}_tmpGFA.nii.gz".format(subject)])
            
            call([animaBinsPath + "animaImageArithmetic", "-i", "{}_tmpAIC.nii.gz".format(subject),
                  "-a", "{}_tmpGFA.nii.gz".format(subject), "-o", "{}_weightAtlas.nii.gz".format(subject)])

            call([animaBinsPath + "animaImageArithmetic", "-i", "{}_weightAtlas.nii.gz".format(subject),
                  "-S", "1", "-M", "-1", 
                  "-o", "{}_weightODF.nii.gz".format(subject)])

            weightEODF = open("{}_weight.txt".format(subject), "a")
            weightEODF.write("{}_weightAtlas.nii.gz\n".format(subject))
            weightEODF.write("{}_weightODF.nii.gz".format(subject))
            weightEODF.close()

            for bundle in bundles:
                  print("BUNDLE {}".format(bundle))
                  os.mkdir("{}".format(bundle))

                  input = open("{}/{}_input.txt".format(bundle, subject), "a")
                  input.write("../../prior/TODs/{0}/average_{0}.nii.gz\n".format(bundle))
                  input.write("{}_ODF_template.nii.gz".format(subject))
                  input.close()

                  call([animaBinsPath + "animaODFAverage", "-i", "{}/{}_input.txt".format(bundle, subject),
                        "-w", "{}_weight.txt".format(subject),
                        "-o", "{}/{}_EODF.nii.gz".format(bundle, subject)])
      os.chdir("..")

      os.chdir("..")


os.chdir('..')