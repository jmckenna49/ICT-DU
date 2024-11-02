'use strict';

const themeSwitcher = document.querySelector('.theme-btn');

// Theme switch functionality
themeSwitcher.addEventListener('click', function() {
    document.body.classList.toggle('light-theme');
    document.body.classList.toggle('dark-theme');

    const className = document.body.className;
    if (className == "light-theme") {
        this.textContent = "Dark";
    } else {
        this.textContent = "Light";
    }

    console.log('current class name: ' + className);
});

// Task management functionality
const taskList = document.getElementById('task-list');
const taskInput = document.getElementById('task-input');
const addTaskBtn = document.getElementById('add-task-btn');

// Function to create a new task item, creating HTML li elements, or list items
function createTaskItem(taskText) {
    const li = document.createElement('li');
    li.classList.add('list');
    li.textContent = taskText;

    // Create remove button for each task
    const removeBtn = document.createElement('button');
    removeBtn.textContent = 'Remove';
    removeBtn.classList.add('remove-btn');
    removeBtn.addEventListener('click', function() {
        taskList.removeChild(li);
    });

    li.appendChild(removeBtn);
    return li;
}

// Add task button functionality
addTaskBtn.addEventListener('click', function() {
    const taskText = taskInput.value;
    if (taskText !== "") {
        const newTask = createTaskItem(taskText);
        taskList.appendChild(newTask);
        taskInput.value = "";  // Clear input after adding
    } else {
        alert("Please enter a task.");
    }
});
