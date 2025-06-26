import javax.swing.*;
import java.awt.*;
import java.awt.event.*;
import java.awt.image.BufferedImage;
import javax.imageio.ImageIO;
import java.io.File;
import java.io.IOException;
import java.util.*;
import java.util.List;

public class HuntTheWumpus extends JFrame implements KeyListener {
    // --- Constants ---
    private static final int SCREEN_WIDTH = 1000;
    private static final int SCREEN_HEIGHT = 1000;
    private static final int NUM_BATS = 2;
    private static final int NUM_PITS = 1;
    private static final int NUM_ARROWS = 3;
    private static final int NUM_ROCKS = 3;

    private static final int UP = 0;
    private static final int DOWN = 1;
    private static final int LEFT = 2;
    private static final int RIGHT = 3;

    private static final Color BROWN = new Color(193, 154, 107);
    private static final Color BLACK = new Color(0, 0, 0);
    private static final Color RED = new Color(138, 7, 7);
    private static final Color GREEN = new Color(0, 255, 64);
    private static final Color WHITE = new Color(255, 255, 255);
    private static final Color YELLOW = new Color(255, 255, 0);
    private static final Color BLUE = new Color(0, 0, 255);
    private static final Color GRAY = new Color(150, 150, 150);
    private static final Color DARK_GRAY = new Color(30, 30, 30);
    private static final Color VERY_DARK_GRAY = new Color(10, 10, 10);
    private static final Color LIGHT_GRAY = new Color(100, 100, 100);
    private static final Color LIGHT_GREEN = new Color(0, 255, 0);
    private static final Color PLAYER_COLOR = new Color(255, 200, 0);

    // --- Cave Layout ---
    private static Map<Integer, int[]> cave = new HashMap<>();
    static {
        cave.put(1, new int[]{0, 8, 2, 5});
        cave.put(2, new int[]{0, 10, 3, 1});
        cave.put(3, new int[]{0, 12, 4, 2});
        cave.put(4, new int[]{0, 14, 5, 3});
        cave.put(5, new int[]{0, 6, 1, 4});
        cave.put(6, new int[]{5, 0, 7, 15});
        cave.put(7, new int[]{0, 17, 8, 6});
        cave.put(8, new int[]{1, 0, 9, 7});
        cave.put(9, new int[]{0, 18, 10, 8});
        cave.put(10, new int[]{2, 0, 11, 9});
        cave.put(11, new int[]{0, 19, 12, 10});
        cave.put(12, new int[]{3, 0, 13, 11});
        cave.put(13, new int[]{0, 20, 14, 12});
        cave.put(14, new int[]{4, 0, 15, 13});
        cave.put(15, new int[]{0, 16, 6, 14});
        cave.put(16, new int[]{15, 0, 17, 20});
        cave.put(17, new int[]{7, 0, 18, 16});
        cave.put(18, new int[]{9, 0, 19, 17});
        cave.put(19, new int[]{11, 0, 20, 18});
        cave.put(20, new int[]{13, 0, 16, 19});
    }

    // --- Game State Variables ---
    private static int player_pos = 0;
    private static int wumpus_pos = 0;
    private static int num_arrows = 1;
    private static int num_rocks = 1;
    private static boolean mobile_wumpus = true;
    private static int wumpus_move_chance = 70;


    private static List<Integer> bats_list = new ArrayList<>();
    private static List<Integer> pits_list = new ArrayList<>();
    private static List<Integer> arrows_list = new ArrayList<>();
    private static List<Integer> rocks_list = new ArrayList<>();

    // Graphics and UI
    private BufferedImage bat_img;
    private BufferedImage player_img;
    private BufferedImage wumpus_img;
    private BufferedImage arrow_img;
    private BufferedImage rock_img;
    private Font font;
    private Random random = new Random();

    // Game state
    private GameState currentState = GameState.MAIN_MENU;


    // Player class


    // Key bindings
    private static Map<String, Integer> keybinds = new HashMap<>();
    static {
        keybinds.put("move_up", KeyEvent.VK_UP);
        keybinds.put("move_down", KeyEvent.VK_DOWN);
        keybinds.put("move_left", KeyEvent.VK_LEFT);
        keybinds.put("move_right", KeyEvent.VK_RIGHT);
        keybinds.put("throw_rock", KeyEvent.VK_R);
        keybinds.put("shoot_arrow", KeyEvent.VK_A);
    }

    // Menu states
    private enum GameState {
        MAIN_MENU, PLAYING, GAME_OVER, SETTINGS, DIFFICULTY, DIRECTION_CHOICE
    }

    // Direction choice state
    private String directionPrompt = "";
    private int selectedDirection = 0;
    private DirectionCallback directionCallback;

    // Settings state
    private String selectedAction = null;
    private String settingsMessage = "";

    // Difficulty state
    private int selectedDifficulty = 0;
    private String[] difficultyOptions = {"Easy", "Medium", "Hard"};

    // Game over state
    private String gameOverMessage = "You have died";

    public HuntTheWumpus() {
        printInstructions();

        // Wait for user input before starting
        JOptionPane.showMessageDialog(null, "Press OK to begin.", "Hunt the Wumpus", JOptionPane.INFORMATION_MESSAGE);

        initializeGame();
        loadImages();
        setupUI();



        setVisible(true);
        requestFocus();
    }

    private void printInstructions() {
        String instructions = """
                             Hunt The Wumpus!
This is the game of "Hunt the Wumpus".  You have been cast into a
dark 20 room cave with a fearsome Wumpus. The cave is shaped like a 
dodachedron and the only way out is to kill the Wumpus.  To that end
you have a bow with one arrow. You might find more arrows from unlucky 
past Wumpus victims in the cave.  There are other dangers in the cave, 
specifcally bats and bottomless pits.

    * If you run out of arrows you die.
    * If you end up in the same room with the Wumpus you die.
    * If you fall into a bottomless pit you die.
    * If you end up in a room with bats they will pick you up
      and deposit you in a random location.

If you are near the Wumpus you will see the bloodstains on the walls.
If you are near bats you will hear them and if you are near a bottomless
pit you will feel the air flowing down it.

If you end up on a red spot the Wumpus will be in one of the following directions
around you <a> key and an selection screen to fire your arrow, if you hit the Wumpus
you win.

If you are unsure where to move you can toss a rock to check if they are Bats, bottomless pits
or the Wumpus by using the <r> key. 
""";
        System.out.println(instructions);
    }

    private void initializeGame() {
        setTitle("Hunt the Wumpus");
        setSize(SCREEN_WIDTH, SCREEN_HEIGHT);
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setResizable(false);
        setLocationRelativeTo(null);

        font = new Font("Arial", Font.BOLD, 36);

        addKeyListener(this);
        setFocusable(true);
    }

    private void loadImages() {
        try {
            bat_img = ImageIO.read(new File("images/bat.png"));
            player_img = ImageIO.read(new File("images/player.png"));
            wumpus_img = ImageIO.read(new File("images/wumpus.png"));
            arrow_img = ImageIO.read(new File("images/arrow.png"));
            rock_img = ImageIO.read(new File("images/rock.png"));
        } catch (IOException e) {
            // Create placeholder images if files don't exist
            bat_img = createPlaceholderImage(50, 50, Color.DARK_GRAY);
            player_img = createPlaceholderImage(40, 40, PLAYER_COLOR);
            wumpus_img = createPlaceholderImage(60, 60, Color.RED);
            arrow_img = createPlaceholderImage(30, 10, Color.GREEN);
            rock_img = createPlaceholderImage(20, 20, Color.GRAY);
        }
    }

    private BufferedImage createPlaceholderImage(int width, int height, Color color) {
        BufferedImage img = new BufferedImage(width, height, BufferedImage.TYPE_INT_ARGB);
        Graphics2D g2d = img.createGraphics();
        g2d.setColor(color);
        g2d.fillOval(0, 0, width, height);
        g2d.dispose();
        return img;
    }

    private void setupUI() {
        // Setup complete - UI will be handled in paint method
    }

    // --- Helper Functions ---
    private boolean checkNeighborRooms(int pos, List<Integer> itemList) {
        int[] exits = cave.get(pos);
        for (int exit : exits) {
            if (itemList.contains(exit)) {
                return true;
            }
        }
        return false;
    }

    private boolean checkNeighborRooms(int pos, int item) {
        int[] exits = cave.get(pos);
        for (int exit : exits) {
            if (exit == item) {
                return true;
            }
        }
        return false;
    }

    @Override
    public void paint(Graphics g) {
        super.paint(g);
        Graphics2D g2d = (Graphics2D) g;
        g2d.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);

        switch (currentState) {
            case MAIN_MENU:
                drawMainMenu(g2d);
                break;
            case PLAYING:
                drawRoom(player_pos, g2d);
                break;
            case GAME_OVER:
                drawGameOver(g2d);
                break;
            case SETTINGS:
                drawSettingsMenu(g2d);
                break;
            case DIFFICULTY:
                drawDifficultyMenu(g2d);
                break;
            case DIRECTION_CHOICE:
                drawDirectionChoice(g2d);
                break;
        }
    }

    private void drawRoom(int pos, Graphics2D g2d) {
        int[] exits = cave.get(player_pos);

        // Fill background
        g2d.setColor(BLACK);
        g2d.fillRect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT);

        // Draw main room circle
        int circleRadius = (int)((SCREEN_WIDTH / 2) * 0.75);
        g2d.setColor(BROWN);
        g2d.fillOval(SCREEN_WIDTH/2 - circleRadius, SCREEN_HEIGHT/2 - circleRadius,
                circleRadius * 2, circleRadius * 2);

        // Draw exits
        int[][] directions = {
                {LEFT, 0, SCREEN_HEIGHT/2-40, SCREEN_WIDTH/4, 80},
                {RIGHT, SCREEN_WIDTH - SCREEN_WIDTH/4, SCREEN_HEIGHT/2-40, SCREEN_WIDTH/4, 80},
                {UP, SCREEN_WIDTH/2-40, 0, 80, SCREEN_HEIGHT/4},
                {DOWN, SCREEN_WIDTH/2-40, SCREEN_HEIGHT - SCREEN_WIDTH/4, 80, SCREEN_HEIGHT/4}
        };

        for (int[] dir : directions) {
            if (exits[dir[0]] > 0) {
                g2d.setColor(BROWN);
                g2d.fillRect(dir[1], dir[2], dir[3], dir[4]);
            }
        }

        // Check if Wumpus is nearby and draw red circle
        if (checkNeighborRooms(player_pos, wumpus_pos)) {
            g2d.setColor(RED);
            int redRadius = (int)((SCREEN_WIDTH/2) * 0.5);
            g2d.fillOval(SCREEN_WIDTH/2 - redRadius, SCREEN_HEIGHT/2 - redRadius,
                    redRadius * 2, redRadius * 2);
        }

        // Draw pit if player is in one
        if (pits_list.contains(player_pos)) {
            g2d.setColor(BLACK);
            int pitRadius = (int)((SCREEN_WIDTH/2) * 0.5);
            g2d.fillOval(SCREEN_WIDTH/2 - pitRadius, SCREEN_HEIGHT/2 - pitRadius,
                    pitRadius * 2, pitRadius * 2);
        }

        // Draw player
        g2d.drawImage(player_img, SCREEN_WIDTH/2 - player_img.getWidth()/2,
                SCREEN_HEIGHT/2 - player_img.getHeight()/2, null);

        // Draw bats if in room
        if (bats_list.contains(player_pos)) {
            g2d.drawImage(bat_img, SCREEN_WIDTH/2 - bat_img.getWidth()/2,
                    SCREEN_HEIGHT/2 - bat_img.getHeight()/2, null);
        }

        // Draw Wumpus if in same room
        if (player_pos == wumpus_pos) {
            g2d.drawImage(wumpus_img, SCREEN_WIDTH/2 - wumpus_img.getWidth()/2,
                    SCREEN_HEIGHT/2 - wumpus_img.getHeight()/2, null);
        }

        // Draw status text
        g2d.setFont(font);
        int y = 50;
        String[] statusLines = {
                "POS: " + player_pos,
                "Arrows: " + num_arrows,
                "Rocks: " + num_rocks,
                checkNeighborRooms(player_pos, bats_list) ? "You hear the squeaking of bats nearby" : "",
                checkNeighborRooms(player_pos, pits_list) ? "You feel a draft nearby" : ""
        };

        for (String line : statusLines) {
            if (!line.isEmpty()) {
                g2d.setColor(GREEN);
                g2d.drawString(line, 10, y);
                y += 50;
            }
        }

        // Handle bat transport message
        if (bats_list.contains(player_pos)) {
            try {
                Thread.sleep(2000);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        }
    }

    private void drawMainMenu(Graphics2D g2d) {
        g2d.setColor(BLACK);
        g2d.fillRect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT);

        g2d.setFont(font);
        String title = "Hunt the Wumpus";
        String start = "Press [S] to Start";
        String settings = "Press [`] for Settings";
        String difficulty = "Press [D] to Change Difficulty";
        String quit = "Press [Q] to Quit";

        g2d.setColor(WHITE);
        drawCenteredString(g2d, title, 150);
        g2d.setColor(LIGHT_GREEN);
        drawCenteredString(g2d, start, 250);
        g2d.setColor(BLUE);
        drawCenteredString(g2d, settings, 300);
        g2d.setColor(YELLOW);
        drawCenteredString(g2d, difficulty, 325);
        g2d.setColor(Color.RED);
        drawCenteredString(g2d, quit, 350);
    }

    private void drawGameOver(Graphics2D g2d) {
        g2d.setColor(RED);
        g2d.fillRect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT);

        g2d.setFont(font);
        g2d.setColor(GREEN);
        drawCenteredString(g2d, gameOverMessage, 200);

        g2d.setColor(WHITE);
        drawCenteredString(g2d, "Press [R] to Retry", 300);
        drawCenteredString(g2d, "Press [M] for Main Menu", 350);
        drawCenteredString(g2d, "Press [Q] to Quit", 400);
    }

    private void drawSettingsMenu(Graphics2D g2d) {
        g2d.setColor(DARK_GRAY);
        g2d.fillRect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT);

        g2d.setFont(font);
        g2d.setColor(WHITE);
        g2d.drawString("Settings - Keybinds", 200, 100);

        int y = 200;
        int idx = 1;
        for (Map.Entry<String, Integer> entry : keybinds.entrySet()) {
            String action = entry.getKey();
            int key = entry.getValue();
            String actionText = "[" + idx + "] " + action.replace("_", " ").toUpperCase() +
                    ": " + KeyEvent.getKeyText(key);

            Color color = action.equals(selectedAction) ? YELLOW : WHITE;
            g2d.setColor(color);
            g2d.drawString(actionText, 200, y);
            y += 50;
            idx++;
        }

        g2d.setColor(GRAY);
        g2d.drawString("Press 1-6 to rebind keys. Press [D] for difficulty. ESC to go back.", 100, 500);

        if (!settingsMessage.isEmpty()) {
            g2d.setColor(LIGHT_GREEN);
            g2d.drawString(settingsMessage, 100, 450);
        }
    }

    private void drawDifficultyMenu(Graphics2D g2d) {
        g2d.setColor(VERY_DARK_GRAY);
        g2d.fillRect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT);

        g2d.setFont(font);
        g2d.setColor(WHITE);
        drawCenteredString(g2d, "Select Difficulty", 100);

        for (int i = 0; i < difficultyOptions.length; i++) {
            Color color = (i == selectedDifficulty) ? LIGHT_GREEN : WHITE;
            g2d.setColor(color);
            drawCenteredString(g2d, difficultyOptions[i], 200 + i * 60);
        }

        g2d.setColor(LIGHT_GRAY);
        drawCenteredString(g2d, "Press ESC to return", 450);
    }

    private void drawDirectionChoice(Graphics2D g2d) {
        g2d.setColor(BLACK);
        g2d.fillRect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT);

        g2d.setFont(font);
        g2d.setColor(WHITE);
        drawCenteredString(g2d, directionPrompt, 100);

        String[] options = {"UP", "DOWN", "LEFT", "RIGHT"};
        for (int i = 0; i < options.length; i++) {
            Color color = (i == selectedDirection) ? LIGHT_GREEN : Color.LIGHT_GRAY;
            g2d.setColor(color);
            drawCenteredString(g2d, options[i], 200 + i * 50);
        }
    }

    private void drawCenteredString(Graphics2D g2d, String text, int y) {
        FontMetrics fm = g2d.getFontMetrics();
        int x = (SCREEN_WIDTH - fm.stringWidth(text)) / 2;
        g2d.drawString(text, x, y);
    }

    private void checkRoom(int pos) {
        if (player_pos == wumpus_pos) {
            gameOver("You were eaten by a WUMPUS!!!");
            return;
        }

        if (pits_list.contains(player_pos)) {
            gameOver("You fell into a bottomless pit!!");
            return;
        }

        if (bats_list.contains(player_pos)) {
            showMessage("Bats pick you up and place you elsewhere in the cave!");
            bats_list.remove(Integer.valueOf(player_pos));
            int newBatPos = random.nextInt(20) + 1;
            while (newBatPos == player_pos) {
                newBatPos = random.nextInt(20) + 1;
            }
            bats_list.add(newBatPos);

            player_pos = random.nextInt(20) + 1;
            while (player_pos == wumpus_pos) {
                player_pos = random.nextInt(20) + 1;
            }
        }

        if (arrows_list.contains(player_pos)) {
            showMessage("You have found an arrow!");
            num_arrows++;
            arrows_list.remove(Integer.valueOf(player_pos));
        }

        if (rocks_list.contains(player_pos)) {
            showMessage("You have found a rock!");
            num_rocks++;
            rocks_list.remove(Integer.valueOf(player_pos));
        }
    }

    private void showMessage(String msg) {
        Graphics2D g2d = (Graphics2D) getGraphics();
        g2d.setColor(BLACK);
        g2d.fillRect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT);

        g2d.setFont(font);
        g2d.setColor(GREEN);
        drawCenteredString(g2d, msg, SCREEN_HEIGHT / 2);

        try {
            Thread.sleep(2500);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }

        repaint();
    }

    private void shootArrow(int direction) {
        if (num_arrows == 0) {
            showMessage("You have no arrows!");
            return;
        }

        num_arrows--;
        animateProjectile(arrow_img, direction);

        if (wumpus_pos == cave.get(player_pos)[direction]) {
            gameOver("Your aim was true and you have killed the Wumpus!");
        } else {
            System.out.println("Your arrow sails into the darkness...");
            placeWumpus();
        }

        if (num_arrows == 0) {
            showMessage("You're out of arrows! The Wumpus begins to hunt you...");
        }
    }

    private void throwRock(int direction) {
        List<String> messages = new ArrayList<>();

        if (num_rocks == 0) {
            messages.add("You have no rocks to throw!");
        } else {
            num_rocks--;
            animateProjectile(rock_img, direction);

            int target = cave.get(player_pos)[direction];
            if (wumpus_pos == target) {
                messages.add("You hear a low growl... the Wumpus is near!");
            } else if (bats_list.contains(target)) {
                messages.add("You hear frantic squeaking... bats!");
            } else if (pits_list.contains(target)) {
                messages.add("You hear the rock fall endlessly... a pit!");
            } else {
                messages.add("You hear a faint clink. The room is empty.");
            }
            if (num_rocks == 0) {
                messages.add("You have no rocks left!");
            }
        }

        Graphics2D g2d = (Graphics2D) getGraphics();
        g2d.setColor(BLACK);
        g2d.fillRect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT);

        g2d.setFont(font);
        g2d.setColor(WHITE);
        int y = 100;
        for (String msg : messages) {
            drawCenteredString(g2d, msg, y);
            y += 50;
        }

        try {
            Thread.sleep(2500);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }

        repaint();
    }

    private void moveWumpus() {
        if (num_arrows > 0) {
            // Passive random movement if arrows still remain
            if (!mobile_wumpus || random.nextInt(100) + 1 > wumpus_move_chance) {
                return;
            }
            int[] neighbors = cave.get(wumpus_pos);
            List<Integer> validMoves = new ArrayList<>();
            for (int room : neighbors) {
                if (room > 0 && room != player_pos && !pits_list.contains(room) && !bats_list.contains(room)) {
                    validMoves.add(room);
                }
            }
            if (!validMoves.isEmpty()) {
                wumpus_pos = validMoves.get(random.nextInt(validMoves.size()));
            }
        } else {
            // Chase player aggressively
            int[] neighbors = cave.get(wumpus_pos);
            for (int room : neighbors) {
                if (room == player_pos) {
                    wumpus_pos = player_pos; // Enters player's room
                    return;
                }
            }

            // Move toward a neighboring room that's closer to the player
            int best = -1;
            int minDiff = 100;
            for (int room : neighbors) {
                if (room > 0 && !pits_list.contains(room) && !bats_list.contains(room)) {
                    int diff = Math.abs(room - player_pos);
                    if (diff < minDiff) {
                        minDiff = diff;
                        best = room;
                    }
                }
            }
            if (best != -1) {
                wumpus_pos = best;
            }
        }
    }

    private void gameOver(String message) {
        gameOverMessage = message;
        currentState = GameState.GAME_OVER;
        repaint();
    }

    private void animateProjectile(BufferedImage image, int direction) {
        int x = SCREEN_WIDTH / 2;
        int y = SCREEN_HEIGHT / 2;

        int dx = 0, dy = 0;
        int speed = 15;
        int steps = 20; // Longer flight

        if (direction == UP) {
            dy = -speed;
        } else if (direction == DOWN) {
            dy = speed;
        } else if (direction == LEFT) {
            dx = -speed;
        } else if (direction == RIGHT) {
            dx = speed;
        }

        for (int i = 0; i < steps; i++) {
            Graphics2D g2d = (Graphics2D) getGraphics();
            drawRoom(player_pos, g2d); // Re-render the base room
            x += dx;
            y += dy;
            g2d.drawImage(image, x - image.getWidth() / 2, y - image.getHeight() / 2, null);

            try {
                Thread.sleep(30);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        }

        repaint();
    }

        private int x = SCREEN_WIDTH / 2;
        private int y = SCREEN_HEIGHT / 2;
        private int speed = 5;
        private Color color = PLAYER_COLOR;
        private int size = 30;

    public void move(int dx, int dy) {
            x += dx * speed;
            y += dy * speed;
            // Keep inside screen bounds
            x = Math.max(0, Math.min(x, SCREEN_WIDTH - size));
            y = Math.max(0, Math.min(y, SCREEN_HEIGHT - size));
        }

        public void draw(Graphics2D g2d) {
            g2d.setColor(color);
            g2d.fillRect(x, y, size, size);
        }

    private void resetGame() {
        num_arrows = 1;
        num_rocks = 2;
        populateCave();
    }

    private void populateCave() {
        bats_list.clear();
        pits_list.clear();
        arrows_list.clear();
        rocks_list.clear();

        player_pos = random.nextInt(20) + 1;
        placeWumpus();
        for (int i = 0; i < NUM_BATS; i++) placeBat();
        for (int i = 0; i < NUM_PITS; i++) placePit();
        for (int i = 0; i < NUM_ARROWS; i++) placeArrow();
        for (int i = 0; i < NUM_ROCKS; i++) placeRock();
    }

    private void placeWumpus() {
        do {
            wumpus_pos = random.nextInt(20) + 1;
        } while (wumpus_pos == player_pos);
    }

    private void placeItem(List<Integer> itemList) {
        int pos;
        do {
            pos = random.nextInt(20) + 1;
        } while (pos == player_pos || pos == wumpus_pos ||
                pits_list.contains(pos) || bats_list.contains(pos) || itemList.contains(pos));
        itemList.add(pos);
    }

    private void placeBat() { placeItem(bats_list); }
    private void placePit() { placeItem(pits_list); }
    private void placeArrow() { placeItem(arrows_list); }
    private void placeRock() { placeItem(rocks_list); }

    private String getActionFromKey(int key) {
        for (Map.Entry<String, Integer> entry : keybinds.entrySet()) {
            if (entry.getValue() == key) {
                return entry.getKey();
            }
        }
        return null;
    }

    // Interface for direction callback
    private interface DirectionCallback {
        void onDirectionChosen(int direction);
    }

    private void chooseDirection(String prompt, DirectionCallback callback) {
        directionPrompt = prompt;
        directionCallback = callback;
        selectedDirection = 0;
        currentState = GameState.DIRECTION_CHOICE;
        repaint();
    }

    @Override
    public void keyPressed(KeyEvent e) {
        int key = e.getKeyCode();
        boolean shiftPressed = (e.getModifiersEx() & KeyEvent.SHIFT_DOWN_MASK) != 0;
        boolean ctrlPressed = (e.getModifiersEx() & KeyEvent.CTRL_DOWN_MASK) != 0;

        switch (currentState) {
            case MAIN_MENU:
                handleMainMenuInput(key);
                break;
            case PLAYING:
                handleGameInput(key, shiftPressed, ctrlPressed);
                break;
            case GAME_OVER:
                handleGameOverInput(key);
                break;
            case SETTINGS:
                handleSettingsInput(key);
                break;
            case DIFFICULTY:
                handleDifficultyInput(key);
                break;
            case DIRECTION_CHOICE:
                handleDirectionChoiceInput(key);
                break;
        }
    }

    private void handleMainMenuInput(int key) {
        if (key == KeyEvent.VK_S) {
            currentState = GameState.PLAYING;
            resetGame();
            repaint();
        } else if (key == KeyEvent.VK_Q) {
            System.exit(0);
        } else if (key == KeyEvent.VK_BACK_QUOTE) {
            currentState = GameState.SETTINGS;
            repaint();
        } else if (key == KeyEvent.VK_D) {
            currentState = GameState.DIFFICULTY;
            repaint();
        }
    }

    private void handleGameInput(int key, boolean shiftPressed, boolean ctrlPressed) {
        if (key == KeyEvent.VK_ESCAPE) {
            System.exit(0);
        }

        String action = getActionFromKey(key);

        if (action != null && action.startsWith("move_")) {
            int direction = -1;
            if (action.equals("move_left")) direction = LEFT;
            else if (action.equals("move_right")) direction = RIGHT;
            else if (action.equals("move_up")) direction = UP;
            else if (action.equals("move_down")) direction = DOWN;

            if (direction != -1) {

                if (shiftPressed) {
                    shootArrow(direction);
                } else if (ctrlPressed) {
                    throwRock(direction);
                } else if (cave.get(player_pos)[direction] > 0) {
                    player_pos = cave.get(player_pos)[direction];
                    moveWumpus();
                    checkRoom(player_pos);
                }
                repaint();
            }
        } else if (action != null && action.equals("throw_rock")) {
            chooseDirection("Choose direction to throw rock", (direction) -> {
                throwRock(direction);
                currentState = GameState.PLAYING;
                repaint();
            });
        } else if (action != null && action.equals("shoot_arrow")) {
            chooseDirection("Choose direction to shoot arrow", (direction) -> {
                shootArrow(direction);
                currentState = GameState.PLAYING;
                repaint();
            });
        }
    }

    private void handleGameOverInput(int key) {
        if (key == KeyEvent.VK_R) {
            resetGame();
            currentState = GameState.PLAYING;
            repaint();
        } else if (key == KeyEvent.VK_M) {
            currentState = GameState.MAIN_MENU;
            resetGame();
            repaint();
        } else if (key == KeyEvent.VK_Q) {
            System.exit(0);
        }
    }

    private void handleSettingsInput(int key) {
        if (selectedAction != null) {
            keybinds.put(selectedAction, key);
            settingsMessage = selectedAction.replace("_", " ").toUpperCase() + " set to " + KeyEvent.getKeyText(key);
            selectedAction = null;
            repaint();
        } else if (key == KeyEvent.VK_ESCAPE) {
            currentState = GameState.MAIN_MENU;
            repaint();
        } else if (key == KeyEvent.VK_1) {
            selectedAction = "move_up";
            repaint();
        } else if (key == KeyEvent.VK_2) {
            selectedAction = "move_down";
            repaint();
        } else if (key == KeyEvent.VK_3) {
            selectedAction = "move_left";
            repaint();
        } else if (key == KeyEvent.VK_4) {
            selectedAction = "move_right";
            repaint();
        } else if (key == KeyEvent.VK_5) {
            selectedAction = "throw_rock";
            repaint();
        } else if (key == KeyEvent.VK_6) {
            selectedAction = "shoot_arrow";
            repaint();
        } else if (key == KeyEvent.VK_D) {
            currentState = GameState.DIFFICULTY;
            repaint();
        }
    }

    private void handleDifficultyInput(int key) {
        if (key == KeyEvent.VK_UP) {
            selectedDifficulty = (selectedDifficulty - 1 + difficultyOptions.length) % difficultyOptions.length;
            repaint();
        } else if (key == KeyEvent.VK_DOWN) {
            selectedDifficulty = (selectedDifficulty + 1) % difficultyOptions.length;
            repaint();
        } else if (key == KeyEvent.VK_ENTER) {
            applyDifficulty(selectedDifficulty);
            currentState = GameState.MAIN_MENU;
            repaint();
        } else if (key == KeyEvent.VK_ESCAPE) {
            currentState = GameState.MAIN_MENU;
            repaint();
        }
    }

    private void handleDirectionChoiceInput(int key) {
        if (key == KeyEvent.VK_UP) {
            selectedDirection = (selectedDirection - 1 + 4) % 4;
            repaint();
        } else if (key == KeyEvent.VK_DOWN) {
            selectedDirection = (selectedDirection + 1) % 4;
            repaint();
        } else if (key == KeyEvent.VK_ENTER) {
            int[] directions = {UP, DOWN, LEFT, RIGHT};
            if (directionCallback != null) {
                directionCallback.onDirectionChosen(directions[selectedDirection]);
            }
        } else if (key == KeyEvent.VK_ESCAPE) {
            currentState = GameState.PLAYING;
            repaint();
        }
    }

    private void applyDifficulty(int difficulty) {
        switch (difficulty) {
            case 0: // Easy
                // NUM_BATS = 1; NUM_PITS = 1; NUM_ARROWS = 5; NUM_ROCKS = 5;
                wumpus_move_chance = 30;
                break;
            case 1: // Medium
                // NUM_BATS = 2; NUM_PITS = 1; NUM_ARROWS = 3; NUM_ROCKS = 3;
                wumpus_move_chance = 60;
                break;
            case 2: // Hard
                // NUM_BATS = 3; NUM_PITS = 2; NUM_ARROWS = 1; NUM_ROCKS = 1;
                wumpus_move_chance = 90;
                break;
        }
    }

    @Override
    public void keyReleased(KeyEvent e) {
        // Not used
    }

    @Override
    public void keyTyped(KeyEvent e) {
        // Not used
    }

    public static void main(String[] args) {
        SwingUtilities.invokeLater(() -> {
            new HuntTheWumpus();
        });
    }
}
