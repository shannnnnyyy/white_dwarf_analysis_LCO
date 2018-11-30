from LCO_data import *
from multiprocessing import Pool
import glob

#global variables
new_data_dir = '/Users/cshanahan/Desktop/WD_project/all_lco_data/new_files_to_sort/'
data_dir = '/Users/cshanahan/Desktop/WD_project/final_ver/23_targs/'
code_dir = '/Users/cshanahan/Desktop/WD_project/scripts/'

def format_path(dirr):

	"""Adds a trailing slash to path name"""
	if dirr[-1] != '/':
		dirr = dirr + '/'
		
	return dirr 
		
def copy_scripts(obj_dir):

	#move required stuff
	reqs = ['daophot.opt','allstar.opt','photo.opt','daophot','allstar','run_daophot.sh', 
			'daomatch', 'daomaster_efo','allframe', 'run_daomatch.sh','run_daomaster_interactive.sh','run_allframe.sh']

	for req in reqs:
		#if not os.path.isfile(obj_dir+req):
		if True:
			#print 'Copying {} to {}.'.format(req,obj_dir)
			shutil.copy(code_dir+req,obj_dir+req)
			
def move_large_FWHM_files(obj_dir,threshold = 7.5):

	obj_dir = format_path(obj_dir)
		
	object_directory = LCODataDir(obj_dir)

	obs_info_tab = object_directory.read_obs_table()
	
	large_fwhm = obs_info_tab[obs_info_tab['med-fwhm'] >= threshold]['#ifile']
	large_fwhm_fwhm = obs_info_tab[obs_info_tab['med-fwhm'] >= threshold]['med-fwhm']
	
	if len(large_fwhm) > 0:
		dest = obj_dir + 'unsucessful/large_fwhm'
		if not os.path.isdir(dest):
			print 'Making directory', obj_dir+'unsucessful/large_fwhm'
			os.makedirs(obj_dir+'unsucessful/large_fwhm')
			
		for i, fit in enumerate(large_fwhm):
			targ = obj_dir + fit + '.fits'
			print 'Moving',targ,' with median FWHM = {} to'.format(large_fwhm_fwhm[i]),dest
			shutil.move(targ, dest)
			
		LCODataDir(dest).make_obs_table()
		
def reset_dirs(obj_dir):

	"""Total reset of object directory. Only original input fits files will remain."""
	
	obj_dir = format_path(obj_dir)

	orig_files = [obj_dir + x + '.fits' for x in LCODataDir(obj_dir).get_input_fits_names()]
	all_files = LCODataDir(obj_dir).get_filenames('*.*')
	rm_files = set(all_files) - set(orig_files)
	
	print 'Deleting output files from {}. '.format(obj_dir)
	for f in rm_files:
		pass
		os.remove(f)
	
	mv_files = []
	#from 'unsucessful' subdirectory
	if os.path.isdir(obj_dir+'unsucessful/failed_daophot'):
		mv_files = LCODataDir(obj_dir+'unsucessful/failed_daophot').get_input_fits_names()
		mv_files = [obj_dir + +'unsucessful/failed_daophot/' + x + '.fits' for x in mv_files]
	if os.path.isdir(obj_dir+'unsucessful/large_fwhm'):
		mv_files = mv_files + LCODataDir(obj_dir+'unsucessful/large_fwhm').get_input_fits_names()
		mv_files = [obj_dir + 'unsucessful/large_fwhm/' + x + '.fits' for x in mv_files]
	
	if len(mv_files) > 0:
		for f in mv_files:
			print f 
			LCOFile(f).move(obj_dir)
	else:
		print 'No files to move.'
	
	if os.path.isdir(obj_dir+'unsucessful'):
		shutil.rmtree(obj_dir + 'unsucessful')
	
	print "{} reset.".format(obj_dir)	
	
		
def run_DAOPhot(obj_dir,reset = False):
	"""Runs shell script that executes DAOPhot on all input fits files in input dir.
		If 'reset' is set to true, files that already have output .psf files will be 
		rerun. Otherwise they will be skipped over and only those with """
		
	obj_dir = format_path(obj_dir)

	os.chdir(obj_dir)
	
	copy_scripts(obj_dir)
	
	fnames = LCODataDir(obj_dir).get_input_fits_names()
	
	if not reset:
		psf_fnames = LCODataDir(obj_dir).get_filenames('s.fits')
		psf_fnames = [os.path.basename(x) for x in psf_fnames]
		if len(psf_fnames) > 0:
			print 'Reset = False :	omitting ', len(psf_fnames), 'files already processed with DAOPhot.'
			psf_fnames = [x.replace('s.fits','') for x in psf_fnames]
			fnames = set(fnames) - set(psf_fnames)
		
		if len(fnames) == 0:
			print 'No new unprocessed files for DAOPhot. Exiting'
			return 
		
	else:		
		if len(fnames) == 0:
			print 'No input files in {}.'.format(obj_dir)
			return

	for fname in fnames:
		os.system('./run_daophot.sh {}'.format(fname))


def move_unsucessful_DAOPhot_files(obj_dir):

	"""Moves files in a directory that didn't sucessfully produce a subtracted image with 
		DAOPhot to a subdirectory named 'unsucessful'."""

	obj_dir = format_path(obj_dir)
	
	object_directory = LCODataDir(obj_dir)
	fits = object_directory.get_input_fits_names()
	sfits = object_directory.get_filenames('s.fits')
	
	dest = obj_dir + 'unsucessful/falied_daophot'
	if not os.path.isdir(obj_dir+'unsucessful/falied_daophot'):
		print 'Making directory', obj_dir+'unsucessful/falied_daophot'
		os.makedirs(obj_dir+'unsucessful/falied_daophot')

	for fit in fits:
		if obj_dir + fit + 's.fits' not in sfits:
			print fit,'not sucessful'
			move_files = object_directory.get_filenames(fit+'*')
			for f in move_files:
				targ = f
				dest = obj_dir + 'unsucessful/falied_daophot'
				print 'Moving',targ,'to',dest
				shutil.move(targ,dest)
				
	LCODataDir(dest).make_obs_table()
	
def run_daomatch(obj_dir):

	os.chdir(obj_dir)

	copy_scripts(obj_dir)

	obs_table = LCODataDir(obj_dir).read_obs_table()
	obs_table.sort('med-fwhm')
	reference_file = obs_table[0]['#ifile']
	other_files = obs_table[1:]['#ifile']
	
	
	str_insert = sorted([other_files[i] for i in range(0,len(other_files))])
	str_insert = '\n'.join(str_insert)+'\n'
	
	lines = []
	with open(obj_dir + 'run_daomatch.sh','r') as f:
		lines =	 f.readlines()
	
	lines[11] = str_insert
	
	with open(obj_dir + 'run_daomatch.sh','w') as f:
		for line in lines:
			f.write(line)

	command = './run_daomatch.sh {} '.format(reference_file)
	os.system(command)

def replace_als_alf(obj_dir):
	os.chdir(obj_dir)
	obs_table = LCODataDir(obj_dir).read_obs_table()
	obs_table.sort('med-fwhm')
	ref_file = obs_table[0]['#ifile']
	print "Replacing .als with .alf in {}".format(ref_file)
	os.system('pwd')
	command = "sed -i -e 's/.als/.alf/g' {}.mch".format(ref_file)
	os.system(command)
	
def run_daomaster(obj_dir,nrun = 1):	

	os.chdir(obj_dir)
	copy_scripts(obj_dir)
	obs_table = LCODataDir(obj_dir).read_obs_table()
	obs_table.sort('med-fwhm')
	ref_file = obs_table[0]['#ifile']
	n_input = str(len(obs_table)-1)
	
	if nrun == 2:
		replace_als_alf(obj_dir)

	command = './run_daomaster_interactive.sh {0} {1}'.format(ref_file,n_input)
	
	print command
	
	os.system(command)
	
def run_allframe(obj_dir):
	os.chdir(obj_dir)
	copy_scripts(obj_dir)
	obs_table = LCODataDir(obj_dir).read_obs_table()
	obs_table.sort('med-fwhm')
	ref_file = obs_table[0]['#ifile']
	command = './run_allframe.sh {0}'.format(ref_file)
	os.system(command)
	
def main_run_LCO_photometry_pipeline(obj_dir, full_reset = False, remake_opt = False,
									rerun_daophot = False):

	if full_reset:
		reset_dirs(obj_dir)

	object_directory = LCODataDir(obj_dir)

	object_directory.make_obs_table()

	move_large_FWHM_files(obj_dir,threshold = 7.5)

	object_directory.get_input_fits_names()

	object_directory.make_obs_table()

	input_fits = object_directory.get_input_fits_names()

	for f in input_fits:
		LCO_obs = LCOFile(obj_dir + f + '.fits')
		LCO_obs.make_opt_file(overwrite = remake_opt)


	run_DAOPhot(dir,reset = rerun_daophot) #SAME HERE 
 	move_unsucessful_DAOPhot_files(obj_dir)
	object_directory.make_obs_table()
	run_daomatch(obj_dir) #SAME HERE
	run_daomaster(obj_dir, nrun = 1) 
	run_allframe(obj_dir)
	run_daomaster(obj_dir,nrun = 2)
 	
	object_directory.make_obs_table()


if __name__ == '__main__':
 			          
	dirs = glob.glob('/Users/cshanahan/Desktop/WD_project/redo_final_ver/other_targs/psf_phot/WD1*')
	dirs = dirs + glob.glob('/Users/cshanahan/Desktop/WD_project/redo_final_ver/other_targs/psf_phot/A*')
	#dirs = ['/Users/cshanahan/Desktop/WD_project/redo_final_ver/other_targs/psf_phot/WD0757-606']
	
	for dir in dirs:
		main_run_LCO_photometry_pipeline(format_path(dir), full_reset = True, remake_opt = False,
										rerun_daophot = False)

	
	

	
