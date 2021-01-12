#!/bin/bash
#
#___INFO__MARK_BEGIN__
##########################################################################
#
#  The Contents of this file are made available subject to the terms of
#  the Sun Industry Standards Source License Version 1.2
#
#  Sun Microsystems Inc., March, 2001
#
#
#  Sun Industry Standards Source License Version 1.2
#  =================================================
#  The contents of this file are subject to the Sun Industry Standards
#  Source License Version 1.2 (the "License"); You may not use this file
#  except in compliance with the License. You may obtain a copy of the
#  License at http://gridengine.sunsource.net/Gridengine_SISSL_license.html
#
#  Software provided under this License is provided on an "AS IS" basis,
#  WITHOUT WARRANTY OF ANY KIND, EITHER EXPRESSED OR IMPLIED, INCLUDING,
#  WITHOUT LIMITATION, WARRANTIES THAT THE SOFTWARE IS FREE OF DEFECTS,
#  MERCHANTABLE, FIT FOR A PARTICULAR PURPOSE, OR NON-INFRINGING.
#  See the License for the specific provisions governing your rights and
#  obligations concerning the Software.
#
#  The Initial Developer of the Original Code is: Sun Microsystems, Inc.
#
#  Copyright: 2001 by Sun Microsystems, Inc.
#
#  All Rights Reserved.
#
##########################################################################
#___INFO__MARK_END__

# ----------------------------------------
#
# example for a load sensor script
#
# Be careful: Load sensor scripts are started with root permissions.
# In an admin_user system euid=0 and uid=admin_user
#

PATH=/bin:/usr/bin


ARCH=`$SGE_ROOT/util/arch`
HOST=`$SGE_ROOT/utilbin/$ARCH/gethostname -name`
function used_space()
{
  # space used in /opt
  space=`df -h /opt | awk ' { print $3 } ' | tail -n1 | cut -f1 -d"G"`
  echo "$space"
}

function total_space()
{
  # total space in /opt
  space=`df -h /opt | awk ' { print $2 } ' | tail -n1 | cut -f1 -d"G"`
  echo "$space"
}

function available_space()
{
  # space available in /opt
  space=`df -h /opt | awk ' { print $4 } ' | tail -n1 | cut -f1 -d"G"`
  echo "$space"
}

function scratch_mounted()
{
  # check if scratch=/opt/uge is mounted; 1=True; 0 = False
  scratch_mounted=`mount  | grep "/opt/uge-8.6.4/default" | wc -l`
  echo "$scratch_mounted"
}

function execd_running()
{
  # Is the execd running
  # Default to registered port if environment variable is undefined
  PORT=${SGE_EXECD_PORT:-6445}
  ! $SGE_ROOT/bin/$ARCH/qping -info $HOST $PORT execd 1 >/dev/null 2>&1
  echo "$?"
}

end=false
while [ $end = false ]; do

   # ----------------------------------------
   # wait for an input
   #
   read input
   result=$?
   if [ $result != 0 ]; then
      end=true
      break
   fi

   if [ "$input" = "quit" ]; then
      end=true
      break
   fi

   # ----------------------------------------
   # send mark for begin of load report
   echo "begin"

   # ----------------------------------------
   # send used_space
   echo "$HOST:opt_used_space:`used_space`"

   # ----------------------------------------
   # send total_space
   echo "$HOST:opt_total_space:`total_space`"

   # ----------------------------------------
   # send available_sapce
   echo "$HOST:opt_avail_space:`available_space`"

   # ----------------------------------------
   # send scratch_mounted
   echo "$HOST:scratch_mounted:`scratch_mounted`"

   # ----------------------------------------
   # send eced_running
   echo "$HOST:execd_running:`execd_running`"

   # ----------------------------------------
   # send mark for end of load report
   echo "end"
done
