# **Social and Assistive Robotics Project setup**

The objectives of this section are:
- Setup the project in student's github
- Review the needed tools
- Update and syncronize the repository project

## **1. Setup the project in student's github**

When working in Laboratory groups, we suggest you:
- One student plays the role of `Director`. This student makes a "Fork" of the Professor's github project.
- The `Director` accept the other students as `Collaborators`

- Then the `Collaborators` will make a "fork" of the `Director`'s github project.
- The `Collaborators` will be able to update the github `Director`'s project and participate on the project generation

- Create in your Laptop a local desired Project/Activity folder. Open VScode in that folder.

### First time

- Clone your forked `Director`'s github project. In `Git bash` VScode terminal, type:
  ```shell
  git clone https://github.com/director_username/Project_Assistive_Robotics
  ```
- Open a "Git bash" terminal and configure git with your credentials:
    ```git
    git config --global user.name "your_name"
    git config --global user.email "your_email@alumnes.ub.edu"
    ```
- You will have to add the folder `.vscode` with your `settings.json` file.

## **2. Update and syncronize the repository project**

When working on a Laboratory project, the objective at the end of a Lab session is to update the changes you have made. 
- Before to work with your local repository, you will have to update it with the `Director` repository. In `Git bash` VScode terminal, type:
    ```shell
    git pull
    ```
- Now you can work on the project. You can create or modify files, add images, etc.
- When you finish your work, you will have to update the `Director` repository with your contributions.
- To add your contributions to the project, you will proceed:
    ````shell
    git add .
    git commit -m "your_commit_message"
    git push
    ````
- You will have to enter your PAT
- The `Director` repository is updated with the collaborator's contributions
