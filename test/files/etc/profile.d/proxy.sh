#!/bin/bash
# 
# cloud node proxy setter
# only set proxy if VM is at BNL
# test success by checking domain of external IP for this host. 
# 
# dig myip.opendns.com @resolver1.opendns.com +short
# wget -q -O - checkip.dyndns.org | sed -e 's/.*Current IP Address: //' -e 's/<.*$//'
#
DEBUG=0

set_bnl_proxy(){
        if [ $DEBUG -eq 1 ] ; then
                echo "Setting BNL proxy vals..."                
        fi
        export http_proxy=http://192.168.1.165:3128
        export https_proxy=http://192.168.1.165:3128
        export ftp_proxy=http://192.168.1.165:3128
        export no_proxy=bnl.gov
}


check_real_ip(){
        REALIP=`wget -q -O - checkip.dyndns.org | sed -e 's/.*Current IP Address: //' -e 's/<.*$//' 2>/dev/null`
        FN=`dig -x $REALIP +short 2>/dev/null `
        if [[ $FN =~ .*bnl.gov.* ]] ; then
                        if [ "$DEBUG" == "1" ] ; then echo "Matches bnl.gov." ; fi
        fi

        if [ $DEBUG -eq 1 ] ; then
                echo "External IP is $REALIP"
                echo "Full name is $FN"
        fi
}

# Main script

if test "${http_proxy+set}" != "set" ; then
        if [ "$DEBUG" == "1" ] ; then echo "http_proxy variable not set, trying Google..." ; fi
                XYZ=`wget -q http://www.google.com -O /dev/null` > /dev/null 2>&1
                RC=$?
                if [ $RC != 0 ] ; then
                        if [ "$DEBUG" == "1" ] ; then echo "Unable to connect outbound, trying proxies..." ; fi
                        set_bnl_proxy
                        check_real_ip
                fi
else
        if [ "$DEBUG" == "1" ] ; then echo "http_proxy var already set" ; fi
fi

