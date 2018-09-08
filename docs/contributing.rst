============
Contributing
============

Thank you for your interest in contributing!
Here are a few steps to get you up and running:

#. Follow the instructions in :doc:`index` to get set up with the
   code base.
#. To run the tests, you will need some more packages. Install them by running
   ``pip install -r requirements_test.txt``
#. Open an issue on
   `GitHub <https://github.com/U8NWXD/batch_crop>`_
   describing the changes you'd like to make. This is important
   because your idea might already be in development or might not
   match existing plans. Reaching
   out to describe your proposal first will help avoid unnecessary
   work. You should also offer to work on it so people know not to
   do it themselves.
#. If your idea is accepted, start working on your idea! You might
   need to ask for suggestions or discuss implementation details in
   the issue first.
#. If you don't have commit access, you'll need to fork the
   repository and then clone your copy instead of the main fork.
#. Create a new branch for your changes:

   .. code-block:: console

     $ git checkout -b your_branch_name

#. Make your changes. Please divide up your work into chunks, each
   of which could be un-done without breaking the app's functionality.
   Make each chunk a commit. Please include comments and documentation
   updates as needed in your changes, preferably in the commit which
   necessitated them. The commit message should follow
   the below style (inspired by `Pro-Git <https://git-scm.com/doc>`_,
   page 127):

   .. code-block:: plain

     Summary on one line and under 70 characters

     After a blank line, you can have paragraphs as needed to more
     fully detail your changes. Wrap them at ~72 lines (no more than
     80) for people viewing it from a command line interface.

     Separate paragraphs with a single line.
       - For bullet points, use hyphens or asterisks
       - You don't need a blank line between bullet points, but you
         should indent multiple lines to create a block of text.

     In your message, describe both what you changed at a high level
     and, more importantly, why you changed it. The rationale is
     important to include because it might not be clear from your
     code changes alone.

#. Test your changes by executing ``./test.sh``. Ideally you won't have broken
   anything, in which case you'll see something like this:

   .. code-block:: console

      ==================== test session starts ====================
      platform darwin -- Python 3.6.5, pytest-3.8.0, py-1.6.0, pluggy-0.7.1
      hypothesis profile 'default' -> database=DirectoryBasedExampleDatabase('batch_crop/.hypothesis/examples')
      rootdir: batch_crop, inifile: pytest.ini
      plugins: cov-2.6.0, hypothesis-3.70.3
      collected 9 items

      batch_crop/batch_crop.py ..                             [ 22%]
      tests/src/test_batch_crop.py .......                    [100%]

      ---------- coverage: platform darwin, python 3.6.5-final-0 -----------
      Name                       Stmts   Miss  Cover
      ----------------------------------------------
      batch_crop/__init__.py         0      0   100%
      batch_crop/batch_crop.py     249    171    31%
      ----------------------------------------------
      TOTAL                        249    171    31%


      ================== 9 passed in 10.07 seconds ==================

      --------------------------------------------------------------------
      Your code has been rated at 10.00/10 (previous run: 10.00/10, +0.00)


      -------------------------------------------------------------------
      Your code has been rated at 10.00/10 (previous run: 9.80/10, +0.20)

   However, things rarely go that well. If there are any problems flagged, make
   the needed changes, add exceptions like
   ``# pylint: disable=missing-docstring``, or change the test case. Be careful
   with the later two, though, and carefully consider whether the behavior you
   are seeing is really correct.

   Ideally, you would write the tests first. This is called test-driven
   development, and it helps you nail down what your code should do before
   starting to write it. This is up to you, though.
#. Add tests that check the changes you made. This helps keep anyone else from
   later breaking your code.
#. Add documentation that describes your changes. Most code can just be
   documented with docstrings (enclosed in triple-quotes), but if you are
   introducing a new concept or abstraction, the ``.rst`` files might need
   updating too. Remember that the code inside methods should rarely need
   documentation to understand what it's doing. Clear code is the best kind of
   documentation!
#. Push your changes:

   .. code-block:: console

     $ git push --set-upstream origin your_branch_name

#. Create a pull request describing your changes and why they were
   made. Use the ``master`` branch as the base for your pull request.
#. Before your pull request can be accepted, it must be reviewed.
   Your reviewer may suggest changes, which you should then make or
   explain why they aren't needed. This is a way to create dialogue
   about changes, which generally enhances code quality.
#. Once your pull request is accepted, you can delete your branch.

