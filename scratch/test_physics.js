            const bounce = 0.7;
            function checkRimCollision(rimX, rimY) {
                let dx = ball.x - rimX;
                let dy = ball.y - rimY;
                let dist = Math.sqrt(dx*dx + dy*dy);
                if (dist < ball.radius + 4) { // 4 is rim thickness
                    let nx = dx / dist;
                    let ny = dy / dist;
                    let p = 2 * (ball.vx * nx + ball.vy * ny);
                    ball.vx = ball.vx - p * nx * bounce;
                    ball.vy = ball.vy - p * ny * bounce;
                    ball.x = rimX + nx * (ball.radius + 4);
                    ball.y = rimY + ny * (ball.radius + 4);
                }
            }
