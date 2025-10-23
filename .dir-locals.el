((nil . (
	 (eval . (progn
		   (message "dir-locals:%s" default-directory)
		   (compile-target-mode 1)
		   t))
	 (compile-target-use-project-el t)
	 (compile-target-targets-list . ((name "dirsize" cmd "python3 src/dirsize/dirsize.py")
					 (name "dircmp" cmd "python3 src/dircmp/dircmp.py")))
	 )))
