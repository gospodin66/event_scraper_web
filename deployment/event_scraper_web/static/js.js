(() => {

document.addEventListener('DOMContentLoaded', function() {
    const ERROR_KEYWORDS = ['error', 'failed', 'failure', 'exception', 'timeout'];
    const btnRun = document.getElementById('btn-fetch-events');
    const buttonText = document.querySelector('.button-text');
    const spinner = document.querySelector('.spinner-border');
    const statusElement = document.getElementById('status');

    const btnShowHosts = document.getElementById('btn-show-hosts');
    const btnUpdateHosts = document.getElementById('btn-update-hosts');
    const hostsTooltip = document.getElementById('tooltip');
    let fromButtonClick = false;

    function isErrorMessage(message) {
        return ERROR_KEYWORDS.some(keyword => 
            message.toLowerCase().includes(keyword)
        );
    }

    function updateTable(events) {
        const tbody = document.querySelector('#output-table tbody');
        tbody.innerHTML = ''; // Clear existing content
        events.forEach(event => {
            const eventRow = document.createElement('tr');
            eventRow.className = 'event-row';
            // Host cell
            const venueHostCell = document.createElement('td');
            venueHostCell.textContent = event.venue;
            eventRow.appendChild(venueHostCell);
            // Venue cell
            const venueNameCell = document.createElement('td');
            venueNameCell.textContent = event.name;
            eventRow.appendChild(venueNameCell);
            // When cell
            const dateCell = document.createElement('td');
            dateCell.textContent = event.when;
            eventRow.appendChild(dateCell);
            // Link cell
            const linkCell = document.createElement('td');
            const link = document.createElement('a');
            link.href = event.link;
            link.textContent = 'View Event';
            link.target = '_blank';
            linkCell.appendChild(link);
            eventRow.appendChild(linkCell);
            // Add row to table
            tbody.appendChild(eventRow);
        });
    }

    function updateStatus(text) {
        statusElement.innerHTML = `${text}`;
        const dots = document.createElement('span');
        dots.className = 'dot'; 
        dots.textContent = ''; 
        statusElement.appendChild(dots);

        let dotCount = 0;
        const interval = setInterval(() => {
            dotCount = (dotCount + 1) % 4;
            dots.textContent = '.'.repeat(dotCount);
        }, 500); 

        if (text.trim() === '') {
            clearInterval(interval);
            statusElement.classList.add('hidden');
            dots.remove();
        } else {
            statusElement.classList.remove('hidden');
        }
    }

    function showStatus(message) {
        statusElement.textContent = message;
        statusElement.id = isErrorMessage(message) ? 'error' : 'status';
    }

    function startTaskPolling(taskId) {
        showStatus("");
        updateStatus("");
        pollTaskStatus(taskId);
    }

    function resetBtn() {
        spinner.classList.add('d-none');
        buttonText.textContent = 'Run Scraper';
        btnRun.disabled = false;
    }

    async function pollTaskStatus(taskId) {
        try {
            const response = await fetch(`/task-status/${taskId}`);
            const data = await response.json();
            
            if (data.state === 'SUCCESS') {
                if (data.result && data.result.status === 'SUCCESS') {
                    showStatus('Task completed');
                    updateTable(data.result.events);
                } else {
                    showStatus('Task failed: ' + data.result.error);
                }
                resetBtn();
            } else if (data.state === 'FAILURE') {
                showStatus('Task failed: ' + data.error);
                resetBtn();
            } else {
                showStatus(data.status);
                updateStatus(data.status, taskId);
                setTimeout(() => pollTaskStatus(taskId), 5000);
            }
        } catch (error) {
            showStatus('Error checking task status: ' + error);
        }
    }

    async function fetchAndDisplayHosts() {
        try {
            const response = await fetch('/get-hosts'); 
            if (response.ok) {
                const hosts = await response.json(); 
                const hostsArray = hosts.hosts || [];
                hostsTooltip.innerHTML = hostsArray.map(host => `<div>${host}</div>`).join('');
                hostsTooltip.style.display = 'block';
            } else {
                hostsTooltip.textContent = 'Error loading hosts';
                hostsTooltip.style.display = 'block';
            }
        } catch (error) {
            hostsTooltip.textContent = 'Error: ' + error.message;
            hostsTooltip.style.display = 'block'; 
        }
    }

    async function updateHosts() {
        const hostsArray = Array.from(hostsTooltip.querySelectorAll('div')).map(div => div.textContent.trim()).filter(line => line !== '');

        if (hostsArray.length > 0) {
            try {
                const response = await fetch('/update-hosts', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ hosts: hostsArray })
                });
                if (response.ok) {
                    console.log('Hosts updated successfully');
                } else {
                    console.error('Error updating hosts:', response.statusText);
                }
            } catch (error) {
                console.error('Error:', error);
            }
        }
    }

    btnShowHosts.addEventListener('click', (e) => {
        fromButtonClick = true;
        hostsTooltip.setAttribute('contenteditable', 'false');
        hostsTooltip.style.left = e.pageX + 'px';
        hostsTooltip.style.top = (e.pageY + 20) + 'px';
        fetchAndDisplayHosts();
    });
    btnUpdateHosts.addEventListener('click', (e) => {
        fromButtonClick = false;
        hostsTooltip.setAttribute('contenteditable', 'true');
        hostsTooltip.style.left = e.pageX + 'px';
        hostsTooltip.style.top = (e.pageY + 20) + 'px';
        fetchAndDisplayHosts();
    });

    hostsTooltip.addEventListener('mouseleave', () => {
        hostsTooltip.style.display = 'none'; 
        if (!fromButtonClick) {
            updateHosts();
        }
        fromButtonClick = false;
    });

    btnShowHosts.addEventListener('mouseleave', () => {
        hostsTooltip.style.display = 'none'; 
    });
    btnShowHosts.addEventListener('mousemove', (e) => {
        if (hostsTooltip.style.display !== 'none') {
            return;
        }
        hostsTooltip.style.left = e.pageX + 'px';
        hostsTooltip.style.top = (e.pageY + 20) + 'px';
    });

    btnRun.addEventListener('click', async function() {
        try {
            document.getElementById('error').textContent = '';
            document.querySelector('#output-table tbody').innerHTML = '';
            spinner.classList.remove('d-none');
            buttonText.textContent = 'Running...';
            this.disabled = true;

            const response = await fetch('/run-scraper', {
                method: 'POST'
            });
            
            const data = await response.json();
            
            if (response.ok) {
                startTaskPolling(data.task_id);
            } else {
                showStatus('Failed to start scraper: ' + data.error);
            }
            
        } catch (error) {
            showStatus('Error: ' + error);
        }
    });

    /** Display events from db if exists */
    fetch('/get-events')
        .then(response => response.json())
        .then(data => {
            if (data.status === 'SUCCESS') {
                updateTable(data.events);
            } else {
                document.getElementById('error').innerText = data.error;
            }
        })
        .catch(error => {
            document.getElementById('error').innerText = 'Error fetching events: ' + error;
        });

});
})();