import re

with open('index.html', 'r') as f:
    content = f.read()

new_html = """
    <!-- Basketball Game Section -->
    <section id="game-section" style="text-align: center; padding: 4rem 2rem; background: var(--secondary); border-top: 1px solid var(--border);">
        <h2 style="color: var(--highlight); margin-bottom: 1.5rem; font-size: 2rem;">Take a Break!</h2>
        <p style="color: var(--text-light); margin-bottom: 2rem; font-size: 1.1rem; line-height: 1.6;">
            Shoot some hoops!<br><br>
            Drag the ball back to aim, and release to shoot.
        </p>
        <div style="margin: 0 auto; max-width: 800px; position: relative;">
            <canvas id="basketballGame" width="800" height="400" style="background: var(--primary); border: 1px solid var(--border); border-radius: 12px; width: 100%; max-width: 800px; height: auto; cursor: crosshair; touch-action: none; display: block; box-shadow: 0 10px 30px rgba(0,0,0,0.5);"></canvas>
            <div id="gameScore" style="position: absolute; top: 15px; left: 20px; font-size: 1.5rem; font-weight: 700; color: var(--highlight); font-family: 'Michroma', sans-serif;">Score: 0</div>
            <div id="gameInstruction" style="position: absolute; top: 15px; right: 20px; font-size: 1rem; color: var(--text-light); opacity: 0.7;">Drag & Release</div>
        </div>
    </section>
"""

content = re.sub(r'<!-- Basketball Game Section -->.*?</section>', new_html.strip(), content, flags=re.DOTALL)

new_js = """
        // Basketball Game Logic
        const gameCanvas = document.getElementById('basketballGame');
        if (gameCanvas) {
            const ctx = gameCanvas.getContext('2d');
            const scoreDisplay = document.getElementById('gameScore');

            let score = 0;
            let gameState = 'AIMING'; // AIMING, FLYING, SCORED, MISSED
            
            const gravity = 0.5;
            const bounce = 0.6;
            const floorFriction = 0.8;

            let ball = {
                startX: 150,
                startY: 320,
                x: 150,
                y: 320,
                radius: 18,
                vx: 0,
                vy: 0
            };

            const hoop = {
                x: 650,
                y: 180,
                radius: 40,
                backboardX: 650 + 40 + 5
            };
            
            let isDragging = false;
            let dragX = 0;
            let dragY = 0;
            let oldBallY = 0;

            function drawBall(x, y) {
                ctx.beginPath();
                ctx.arc(x, y, ball.radius, 0, Math.PI * 2);
                ctx.fillStyle = '#ff8c00';
                ctx.fill();
                ctx.closePath();
                
                ctx.beginPath();
                ctx.strokeStyle = '#333';
                ctx.lineWidth = 1.5;
                ctx.moveTo(x - ball.radius, y);
                ctx.lineTo(x + ball.radius, y);
                ctx.stroke();
                
                ctx.beginPath();
                ctx.moveTo(x, y - ball.radius);
                ctx.lineTo(x, y + ball.radius);
                ctx.stroke();
            }

            function drawHoopBack() {
                // Pole
                ctx.fillStyle = '#444';
                ctx.fillRect(hoop.backboardX, hoop.y - 40, 15, 300);
                
                // Backboard
                ctx.fillStyle = 'rgba(255, 255, 255, 0.9)';
                ctx.fillRect(hoop.backboardX - 10, hoop.y - 70, 15, 100);
                
                // Back rim
                ctx.beginPath();
                ctx.ellipse(hoop.x, hoop.y, hoop.radius, 12, 0, Math.PI, Math.PI * 2);
                ctx.strokeStyle = '#ef4444';
                ctx.lineWidth = 4;
                ctx.stroke();
            }
            
            function drawHoopFront() {
                // Front rim
                ctx.beginPath();
                ctx.ellipse(hoop.x, hoop.y, hoop.radius, 12, 0, 0, Math.PI);
                ctx.strokeStyle = '#ef4444';
                ctx.lineWidth = 4;
                ctx.stroke();
                
                // Net
                ctx.beginPath();
                ctx.strokeStyle = 'rgba(255, 255, 255, 0.4)';
                ctx.lineWidth = 2;
                ctx.moveTo(hoop.x - hoop.radius, hoop.y);
                ctx.lineTo(hoop.x - hoop.radius + 15, hoop.y + 60);
                ctx.lineTo(hoop.x + hoop.radius - 15, hoop.y + 60);
                ctx.lineTo(hoop.x + hoop.radius, hoop.y);
                
                // Net criss-cross
                for(let i=1; i<4; i++) {
                    ctx.moveTo(hoop.x - hoop.radius + (i*8), hoop.y);
                    ctx.lineTo(hoop.x - hoop.radius + 15 + (i*5), hoop.y + 60);
                    
                    ctx.moveTo(hoop.x + hoop.radius - (i*8), hoop.y);
                    ctx.lineTo(hoop.x + hoop.radius - 15 - (i*5), hoop.y + 60);
                }
                
                ctx.stroke();
            }

            function drawTrajectory() {
                if (isDragging && gameState === 'AIMING') {
                    ctx.beginPath();
                    ctx.strokeStyle = 'rgba(255, 255, 255, 0.4)';
                    ctx.setLineDash([5, 5]);
                    ctx.lineWidth = 2;
                    
                    let tx = ball.x;
                    let ty = ball.y;
                    let tvx = (ball.x - dragX) * 0.18;
                    let tvy = (ball.y - dragY) * 0.18;
                    
                    ctx.moveTo(tx, ty);
                    for (let i = 0; i < 25; i++) {
                        tx += tvx;
                        tvy += gravity;
                        ty += tvy;
                        ctx.lineTo(tx, ty);
                    }
                    ctx.stroke();
                    ctx.setLineDash([]);
                }
            }

            function checkRimCollision(rimX, rimY) {
                let dx = ball.x - rimX;
                let dy = ball.y - rimY;
                let dist = Math.sqrt(dx*dx + dy*dy);
                if (dist < ball.radius + 4) {
                    let nx = dx / dist;
                    let ny = dy / dist;
                    let p = 2 * (ball.vx * nx + ball.vy * ny);
                    ball.vx = ball.vx - p * nx * bounce;
                    ball.vy = ball.vy - p * ny * bounce;
                    ball.x = rimX + nx * (ball.radius + 4);
                    ball.y = rimY + ny * (ball.radius + 4);
                }
            }

            function updateGame() {
                ctx.clearRect(0, 0, gameCanvas.width, gameCanvas.height);
                
                // Draw floor
                ctx.fillStyle = 'rgba(255, 255, 255, 0.05)';
                ctx.fillRect(0, 380, gameCanvas.width, 20);
                
                drawHoopBack();
                
                if (gameState === 'FLYING' || gameState === 'SCORED' || gameState === 'MISSED') {
                    oldBallY = ball.y;
                    
                    ball.vy += gravity;
                    ball.x += ball.vx;
                    ball.y += ball.vy;
                    
                    // Left rim collision
                    checkRimCollision(hoop.x - hoop.radius, hoop.y);
                    // Right rim collision
                    checkRimCollision(hoop.x + hoop.radius, hoop.y);
                    
                    // Backboard collision
                    if (ball.x + ball.radius > hoop.backboardX - 10 && ball.x - ball.radius < hoop.backboardX + 5) {
                        if (ball.y > hoop.y - 70 && ball.y < hoop.y + 30) {
                            if (ball.vx > 0) {
                                ball.vx *= -bounce;
                                ball.x = hoop.backboardX - 10 - ball.radius;
                            }
                        }
                    }
                    
                    // Floor collision
                    if (ball.y + ball.radius > 380) {
                        ball.y = 380 - ball.radius;
                        ball.vy *= -bounce;
                        ball.vx *= floorFriction;
                    }
                    
                    // Score logic: ball goes down through the hoop
                    if (gameState === 'FLYING' && oldBallY < hoop.y && ball.y >= hoop.y && ball.vy > 0) {
                        if (ball.x > hoop.x - hoop.radius + 5 && ball.x < hoop.x + hoop.radius - 5) {
                            score++;
                            scoreDisplay.textContent = 'Score: ' + score;
                            gameState = 'SCORED';
                            setTimeout(resetBall, 1500);
                        }
                    }
                    
                    // Miss check: if ball stops moving or falls out of bounds
                    if (gameState === 'FLYING') {
                        if ((Math.abs(ball.vx) < 0.1 && Math.abs(ball.vy) < 0.1 && ball.y > 370) || ball.x < -50 || ball.x > gameCanvas.width + 50) {
                            gameState = 'MISSED';
                            setTimeout(resetBall, 1000);
                        }
                    }
                }
                
                // Draw the ball behind the front rim if it's "inside" the basket area
                drawBall(ball.x, ball.y);
                drawHoopFront();
                drawTrajectory();
                
                if (isDragging && gameState === 'AIMING') {
                    // Draw a subtle line from ball to pull point
                    ctx.beginPath();
                    ctx.moveTo(ball.x, ball.y);
                    ctx.lineTo(dragX, dragY);
                    ctx.strokeStyle = 'rgba(255, 140, 0, 0.5)';
                    ctx.lineWidth = 3;
                    ctx.stroke();
                }
                
                if (gameState === 'SCORED') {
                    ctx.fillStyle = '#10b981';
                    ctx.font = 'bold 36px "Michroma", sans-serif';
                    ctx.fillText('SWISH!', gameCanvas.width/2 - 70, 100);
                } else if (gameState === 'MISSED') {
                    ctx.fillStyle = '#ef4444';
                    ctx.font = 'bold 36px "Michroma", sans-serif';
                    ctx.fillText('MISS!', gameCanvas.width/2 - 50, 100);
                }
                
                requestAnimationFrame(updateGame);
            }

            function resetBall() {
                ball.x = ball.startX;
                ball.y = ball.startY;
                ball.vx = 0;
                ball.vy = 0;
                gameState = 'AIMING';
            }

            function getMousePos(e) {
                const rect = gameCanvas.getBoundingClientRect();
                const scaleX = gameCanvas.width / rect.width;
                const scaleY = gameCanvas.height / rect.height;
                const clientX = e.touches ? e.touches[0].clientX : e.clientX;
                const clientY = e.touches ? e.touches[0].clientY : e.clientY;
                return {
                    x: (clientX - rect.left) * scaleX,
                    y: (clientY - rect.top) * scaleY
                };
            }

            function handleStart(e) {
                if (gameState !== 'AIMING') return;
                const pos = getMousePos(e);
                
                isDragging = true;
                dragX = pos.x;
                dragY = pos.y;
                
                if (e.touches) e.preventDefault();
            }

            function handleMove(e) {
                if (!isDragging) return;
                const pos = getMousePos(e);
                dragX = pos.x;
                dragY = pos.y;
                if (e.touches) e.preventDefault();
            }

            function handleEnd(e) {
                if (!isDragging) return;
                isDragging = false;
                
                let dx = ball.x - dragX;
                let dy = ball.y - dragY;
                
                ball.vx = dx * 0.18;
                ball.vy = dy * 0.18;
                
                if (Math.abs(ball.vx) > 1 || Math.abs(ball.vy) > 1) {
                    gameState = 'FLYING';
                }
            }

            gameCanvas.addEventListener('mousedown', handleStart);
            gameCanvas.addEventListener('mousemove', handleMove);
            window.addEventListener('mouseup', handleEnd);
            
            gameCanvas.addEventListener('touchstart', handleStart, {passive: false});
            gameCanvas.addEventListener('touchmove', handleMove, {passive: false});
            window.addEventListener('touchend', handleEnd);

            resetBall();
            updateGame();
        }
"""

content = re.sub(r'// Basketball Game Logic.*?}\s*</script>', new_js.strip() + '\n    </script>', content, flags=re.DOTALL)

with open('index.html', 'w') as f:
    f.write(content)
