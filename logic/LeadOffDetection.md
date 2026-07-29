
1. Arduino cameras capture base + runner foot
2. Python detects foot + base
  a. Use YOLO11 Bag Detection Model (https://universe.roboflow.com/baseball-r7dzp/detect-baseballs) + KeyPoint Pose Capture (YOLO-Pose, Mediapipe, OpenCV)
3. Python calculates distance
  a. Use Frame to Frame (F2F) Filtering to maximize accurate path while also not compromising speed, including:
    i. Exponential Moving Average (EMA)
    ii. Kalman Filters
  b. This system will be presented + prototyped in Python but Accelerated by conversion to c++
4. Python sends JSON to Unity
  a. Create Json but only send if it hits a certain threshold during any given pitch
    i. Basically, continuously rewrite over the same file until distance exceeds certain amount
  b. Raise Flag in Unity upon first protocol continue exceeding certain distance
5. Unity updates HUD
  a. Red Text Flashes twice telling them to watch
6. Unity triggers alert + audio
  a. Max Distance update
7. Cut Max Distance updating + alert text as soon as motion starts
  a. When Gyroscopic sensor in camera recognizes load/cockback/exceeding force, it can assume the motion has started and the batter is taking their secondary lead

6b Bonus. If extension camera plotting pitcher pose recognizes pitcher_lead_leg && pitcher_lead_foot is increasing in height aka (lifting his knee)
  a. If itcher_lead_leg is at vertex && If dLead/dt or runner_side_knee/arm/hips appear to rotate and arms cock back -> Assume runner is stealing
    i. If runner is on first going to two:
      I. Pitcher is Righty -> Alert Catcher
      II. Pitcher is Lefty -> Alert Pitcher Pick Off 1b
    ii. If runner is on second going to three:
      I. Always alert Pitcher for inside move

  b. If pitcher_lead_leg is lowering && If dLead/dt or runner_side_knee/arm/hips appear to rotate and arms cock back -> Assume runner is stealing and alert catcher + bag to throw to

(6b Bonus)c. Include a cam pointed towards the plate for the following:
  a. Display actual pitch location (where it ended up)
  b. Use no pitch detected in conjunction with irregular YOLO delivery expectations (AKA a pickoff) to not count that into total pitch count.
