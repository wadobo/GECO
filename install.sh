#!/bin/bash

function install_help(){
		echo "Ayuda del instalador $(basename $0)"
                echo "   Con este instalador puedes instalar:"
                echo "     gecod"
                echo "     gecoc"
                echo "     gtk-geco"
                echo "     web-geco"
                echo ""
                echo " Usalo pasando como argumento el nombre de lo que quieras instalar"
                echo " por ejemplo:"
                echo "    sudo ./$(basename $0) gecod"
}

root=$PWD

if [ "$#" -eq 0 ]
then
    install_help
    exit 0
fi

while [ "$#" -gt 0 ]
do
	case $1 in
	-h | --help)
        install_help
		shift
		;;
	gecod)
        cd $root
        cd src/gecod/
        echo "instalando gecod"
        python setup.py install
		shift
		;;
	gecoc)
        cd $root
        cd src/gecoc/
        echo "instalando gecoc"
        python setup.py install
		shift
		;;
	gtk-geco)
        cd $root
        cd src/gecoc/
        echo "instalando gecoc"
        python setup.py install
        cd $root
        cd src/gecoc/gtk-geco
        echo "instalando gtk-geco"
        python setup.py install
		shift
		;;
	web-geco)
        cd $root
        cd src/gecoc/
        echo "instalando gecoc"
        python setup.py install
        cd $root
        cd src/gecoc/web-geco
        echo "instalando web-geco"
        python setup.py install
		shift
		;;
	*)  
        install_help
		shift
		;;
	esac
done

