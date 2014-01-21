#!/bin/env python
#
#
# Top level build tool
#
# imgfac-build  TDL_FILE  [ TDL_FILE ]
#
# Execute with one or more TDL files. 
#  
# For each <filename>.tdl checks to see if there is a <filename>.files.yaml
# If so, it runs embed-files against the yaml, creating <filename>.files.tdl 
#
# It then runs merge-tdls against the input list, substitution <filename>.withfiles.tdl where
# appropriate. Latter TDLs override equivalent content in earlier TDLs. 

