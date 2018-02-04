
include Make.rules

# dynamically find the files we need, recursivly...
APT_SRC_DIRS=$(shell find etc/apt -type d)
APT_DEST_DIRS=$(addprefix ${BUILD_DIR}/, ${APT_SRC_DIRS} )
APT_SRC_FILES=$(shell find etc/apt -type f)
APT_DEST_FILES=$(addprefix ${BUILD_DIR}/, ${APT_SRC_FILES} )

.PHONY: clean all pkgs clean distclean print 

# expand this to multiple targets..
define DIR_TARGET =
${BUILD_DIR}/${1}:
	mkdir -p $$@
endef

define FILE_PATH_TARGET
${BUILD_DIR}/${1}: ${1}
	cp $$< $$@
endef

all: pkgs

pkgs:  ${APT_DEST_DIRS} ${APT_DEST_FILES}



# expand out individual rules for each directory.
$(foreach d, ${APT_SRC_DIRS},$(eval $(call DIR_TARGET,$d)))
$(foreach d, ${APT_SRC_FILES},$(eval $(call FILE_PATH_TARGET,$d)))

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


