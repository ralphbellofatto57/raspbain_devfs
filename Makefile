
include Make.rules

# dynamically find the files we need, recursivly...
APT_SRC_DIRS=$(shell find etc/apt -type d)
#APT_DEST_DIRS=$(addprefix ${BUILD_DIR}/, ${APT_SRC_DIRS} )
APT_SRC_FILES=$(shell find etc/apt -type f)
#APT_DEST_FILES=$(addprefix ${BUILD_DIR}/, ${APT_SRC_FILES} )

.PHONY: clean all pkgs clean distclean print 

# expand this to multiple targets..
define DIR_TARGET =
${BUILD_DIR}/${1}:
	mkdir -p $$@
endef

REPO_PKG_FILES=
REPO_PKG_FILES+='${BUILD_DIR}/aptcache/archive.raspberrypi.org/debian/main/binary-armhf/Packages'
REPO_PKG_FILES+='${BUILD_DIR}/aptcache/archive.raspberrypi.org/debian/ui/binary-armhf/Packages'
REPO_PKG_FILES+='${BUILD_DIR}./aptcache/mirrordirector.raspbian.org/raspbian/contrib/binary-armhf/Packages'
REPO_PKG_FILES+='${BUILD_DIR}./aptcache/mirrordirector.raspbian.org/raspbian/main/binary-armhf/Packages'
REPO_PKG_FILES+='${BUILD_DIR}./aptcache/mirrordirector.raspbian.org/raspbian/non-free/binary-armhf/Packages'
REPO_PKG_FILES+='${BUILD_DIR}./aptcache/mirrordirector.raspbian.org/raspbian/rpi/binary-armhf/Packages'

PKGS=
PKGS=pigpio


define FILE_PATH_TARGET
${BUILD_DIR}/${1}: ${1}
	cp $$< $$@
endef

all: ${BUILD_DIR}/apt-install.done


# we could get more detailed by doing one package at a time
# based on a senitle file.
${BUILD_DIR}/apt-install.done: ${BUILD_DIR}/pkgfiles.done
	./apt-install.py --cache ${BUILD_DIR}/aptcache --outdir ${BUILD_DIR} ${PKGS}
	touch $@


# not quite a complete description because if the repositories change
# then will need to update date, do do that one has to do an apt or do update 
# target
${BUILD_DIR}/pkgfiles.done: ${APT_SRC_DIRS}
	./apt-install.py --cache ${BUILD_DIR}/aptcache --outdir ${BUILD_DIR} --update --noinstall
	touch $@

update:
	./apt-install.py --cache ${BUILD_DIR}/aptcache --outdir ${BUILD_DIR} --update

#pkgs:  ${APT_DEST_DIRS} ${APT_DEST_FILES}


# keep as reference...
# expand out individual rules for each directory.
#$(foreach d, ${APT_SRC_DIRS},$(eval $(call DIR_TARGET,$d)))
#$(foreach d, ${APT_SRC_FILES},$(eval $(call FILE_PATH_TARGET,$d)))

${BUILD_DIR}:
	$@ mkdir -p ${BUILD_DIR}

${BUILD_DIR}/etc/apt:
	echo mkdir -p $@


clean:
	@rm -rf ${BUILD_DIR}

distclean: clean
	@rm -rf Make.rules

print:
	@echo TOP_DIR=${TOP_DIR}
	@echo BUILD_DIR=${BUILD_DIR}
	@echo APT_SRC_DIRS=${APT_SRC_DIRS}
	@echo APT_DEST_DIRS=${APT_DEST_DIRS}
	@echo bindir=${bindir}
	@echo REPO_PKG_FILES=${REPO_PKG_FILES}
	@echo PKGS=${PKGS}


