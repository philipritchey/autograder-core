BASE_DIR=$(pwd)

if [ -d /autograder ]; then
  # we are in a gradescope-like environment
  AUTOGRADER_CORE_REPO=/autograder/autograder-core
  REPO=/autograder/autograder-code
  SUBMISSION=/autograder/submission

  # Update autograder files
  cd $AUTOGRADER_CORE_REPO
  git pull
  cd $REPO
  git pull
  cd $BASE_DIR

else
  # we are NOT in a gradescope-like environment
  AUTOGRADER_CORE_REPO=$BASE_DIR/../autograder-core
  REPO=$BASE_DIR
  SUBMISSION=$BASE_DIR/solution

fi

# copy provided files into submission directory
for file in "${provided_files[@]}"; do
    cp $REPO/provided/$file $SUBMISSION/
done

# bootstrapping FTW
cp $AUTOGRADER_CORE_REPO/run_autograder_script.sh ras
chmod u+x ./ras
./ras "${files_to_submit[@]}" "${provided_files[@]}"

rm ras
