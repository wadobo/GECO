#! /bin/sh

PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin
DAEMON=/usr/bin/gecod-xmlrpc
NAME=gecod
DESC=gecod

test -x $DAEMON || exit 0

LOGDIR=/var/log/gecod
PIDFILE=/var/run/gecod-xmlrpc.pid
DODTIME=1                   # Time to wait for the server to die, in seconds
                            # If this value is set too low you might not
                            # let some servers to die gracefully and
                            # 'restart' will not work

# Include gecod defaults if available
if [ -f /etc/default/gecod ] ; then
	. /etc/default/gecod
fi

set -e

running_pid()
{
    # Check if a given process pid's cmdline matches a given name
    pid=$1
    name=$2
    [ -z "$pid" ] && return 1
    [ ! -d /proc/$pid ] &&  return 1
    return 0
}

running()
{
# Check if the process is running looking at /proc
# (works for all users)

    # No pidfile, probably no daemon present
    [ ! -f "$PIDFILE" ] && return 1
    # Obtain the pid and check it against the binary name
    pid=`cat $PIDFILE`
    running_pid $pid $DAEMON || return 1
    return 0
}

gecodstop()
{
    [ ! -f "$PIDFILE" ] && return 0
    kill -9 $(cat $PIDFILE)
    rm $PIDFILE
}

force_stop() {
# Forcefully kill the process
    [ ! -f "$PIDFILE" ] && return
    if running ; then
        kill -15 $pid
        # Is it really dead?
        [ -n "$DODTIME" ] && sleep "$DODTIME"s
        if running ; then
            kill -9 $pid
            [ -n "$DODTIME" ] && sleep "$DODTIME"s
            if running ; then
                echo "Cannot kill $LABEL (pid=$pid)!"
                exit 1
            fi
        fi
    fi
    rm -f $PIDFILE
    return 0
}

case "$1" in
  start)
	echo -n "Starting $DESC: "
	start-stop-daemon --start --quiet --pidfile $PIDFILE \
		--exec $DAEMON -- $DAEMON_OPTS
        if running ; then
            echo "$NAME."
        else
            echo " ERROR."
        fi
	;;
  stop)
	echo -n "Stopping $DESC: "
    gecodstop
	echo "$NAME."
	;;
  restart)
    echo -n "Restarting $DESC: "
    gecodstop
	start-stop-daemon --start --quiet --pidfile \
		/var/run/$NAME.pid --exec $DAEMON -- $DAEMON_OPTS
	echo "$NAME."
	;;
  force-reload)
    echo -n "Restarting $DESC: "
    gecodstop
	start-stop-daemon --start --quiet --pidfile \
		/var/run/$NAME.pid --exec $DAEMON -- $DAEMON_OPTS
	echo "$NAME."
	;;
  status)
    echo -n "$LABEL is "
    if running ;  then
        echo "running"
    else
        echo " not running."
        exit 1
    fi
    ;;
  *)
	N=/etc/init.d/$NAME
	# echo "Usage: $N {start|stop|restart}" >&2
	echo "Usage: $N {start|stop|restartstatus}" >&2
	exit 1
	;;
esac

exit 0
