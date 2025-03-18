console.log('%c SCRIPT.JS LOADED SUCCESSFULLY! ', 'background: #222; color: #bada55; font-size: 20px');

document.addEventListener('DOMContentLoaded', function() {
    console.log("DOM fully loaded and parsed");
    
    // SIMPLIFIED VERSION - Just focus on fixing the modal
    const video = document.getElementById('wedding-video');
    const tapAnimation = document.getElementById('tap-animation');
    
    // Handle tap to unmute (only if elements exist)
    if (video) {
        video.addEventListener('click', function() {
            if (video.muted) {
                video.muted = false;
                if (tapAnimation) tapAnimation.style.display = 'none';
            }
        });
    }
    
    // Fix Modal Functionality
    const modal = document.getElementById('rsvp-modal');
    const rsvpBtn = document.getElementById('rsvp-btn');
    const closeBtn = document.querySelector('.close');
    const rsvpForm = document.getElementById('rsvp-form');
    const submitBtn = document.getElementById('rsvp-submit-btn');
    
    console.log("Modal elements:", {
        modal: modal,
        rsvpBtn: rsvpBtn,
        closeBtn: closeBtn,
        rsvpForm: rsvpForm,
        submitBtn: submitBtn
    });
    
    // Open modal - THIS IS THE KEY PART
    if (rsvpBtn) {
        console.log("Adding click handler to I'M DEFINITELY IN button");
        rsvpBtn.addEventListener('click', function(e) {
            console.log("RSVP button clicked!");
            if (modal) {
                console.log("Setting modal display to block");
                modal.style.display = 'block';
            } else {
                console.error("Modal element not found!");
            }
        });
    }
    
    // Close modal with X button
    if (closeBtn) {
        closeBtn.addEventListener('click', function() {
            console.log("Closing modal");
            if (modal) modal.style.display = 'none';
        });
    }
    
    // Close modal when clicking outside
    window.addEventListener('click', function(event) {
        if (modal && event.target === modal) {
            console.log("Closing modal (clicked outside)");
            modal.style.display = 'none';
        }
    });
    
    // Handle form submission
    if (submitBtn) {
        submitBtn.addEventListener('click', function() {
            console.log("Submit button clicked!");
            
            const familyName = document.getElementById('family-name').value.trim();
            const guestCount = document.getElementById('guest-count').value.trim();
            // Get the sheet ID if it's available in the page
            const sheetId = document.querySelector('meta[name="sheet-id"]')?.getAttribute('content') || null;
            
            console.log(`FORM SUBMIT: Preparing to send RSVP for ${familyName}, ${guestCount} guests, Sheet ID: ${sheetId}`);
            
            if (!familyName) {
                alert('Please enter your full name.');
                return;
            }
            
            if (!guestCount || guestCount < 1) {
                alert('Please enter a valid number of guests.');
                return;
            }
            
            // Show a submission indicator
            const originalText = submitBtn.textContent;
            submitBtn.textContent = 'Submitting...';
            submitBtn.disabled = true;
            
            fetch('/submit_rsvp', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    familyName: familyName,
                    guestCount: guestCount,
                    sheetId: sheetId
                })
            })
            .then(response => response.text())
            .then(text => {
                console.log('Raw response:', text);
                try {
                    return JSON.parse(text);
                } catch (e) {
                    console.error('Parse error:', e);
                    return { success: false, error: 'Invalid JSON response' };
                }
            })
            .then(data => {
                console.log('Response data:', data);
                if (data && data.success) {
                    alert('RSVP submitted successfully!');
                    if (modal) modal.style.display = 'none';
                    if (rsvpForm) rsvpForm.reset();
                } else {
                    alert('Error: ' + (data && data.error ? data.error : 'Unknown error'));
                }
            })
            .catch(err => {
                console.error('Network error:', err);
                alert('Error: ' + err);
            })
            .finally(() => {
                submitBtn.textContent = originalText;
                submitBtn.disabled = false;
            });
        });
    }
});

// Global test function for console debugging
window.testRSVP = function(name, count) {
    console.log(`Manual test: ${name}, ${count}`);
    fetch('/submit_rsvp', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            familyName: name || 'Test Person',
            guestCount: count || '2'
        })
    })
    .then(r => r.text())
    .then(t => console.log(t));
};

// Countdown Timer
function updateCountdown() {
    const weddingDate = new Date('2025-04-13T09:00:00-05:00'); // 9 AM CST on April 13, 2025
    const now = new Date();
    
    // Get total seconds between the times
    const totalSeconds = Math.floor((weddingDate - now) / 1000);
    
    // If the date has passed
    if (totalSeconds <= 0) {
        document.getElementById('countdown-days').textContent = '0';
        document.getElementById('countdown-hours').textContent = '0';
        document.getElementById('countdown-minutes').textContent = '0';
        document.getElementById('countdown-seconds').textContent = '0';
        return;
    }
    
    // Calculate days, hours, minutes, seconds
    const days = Math.floor(totalSeconds / 86400);
    const hours = Math.floor((totalSeconds % 86400) / 3600);
    const minutes = Math.floor((totalSeconds % 3600) / 60);
    const seconds = Math.floor(totalSeconds % 60);
    
    // Update the countdown
    document.getElementById('countdown-days').textContent = days;
    document.getElementById('countdown-hours').textContent = hours;
    document.getElementById('countdown-minutes').textContent = minutes;
    document.getElementById('countdown-seconds').textContent = seconds;
}

// Call immediately and set up interval
updateCountdown();
setInterval(updateCountdown, 1000); 