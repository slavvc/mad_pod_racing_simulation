#include <iostream>
#include <string>
#include <vector>
#include <algorithm>
#include <math.h>

using namespace std;

/**
 * Auto-generated code below aims at helping you parse
 * the standard input according to the problem statement.
 **/
double k = 2.5;
int checkpoint_radius = k*600;
int force_field = k*400;

enum class GameCondition: int
{
    FAR_FROM_ALL = 0,
    CLOSE_TO_CHECKPOINT_ONLY = 1,
    CLOSE_TO_OPPONENT_ONLY = 2,
    CLOSE_TO_ALL = 3,
};

struct GameState
{
    int x = 0;
    int y = 0;

    int next_checkpoint_x = 0; // x position of the next check point
    int next_checkpoint_y = 0; // y position of the next check point

    int opponent_x = 0;
    int opponent_y = 0;
    
    int next_checkpoint_dist = 0; // distance to the next checkpoint
    
    int next_checkpoint_angle = 0; // angle between your pod orientation and the direction of the next checkpoint

    int opponent_dist = 0; // distance to the opponent       
    int opponent_checkpoint_dist = 0; // distance between the next checkpoint and the opponent

    GameCondition game_condition = GameCondition::FAR_FROM_ALL;
};

int main()
{
    int boost_used = false;

    auto get_thrust_input = [boost_used](const GameState & s) -> std::string
        {
            int thrust = (s.next_checkpoint_angle > 90 || s.next_checkpoint_angle < -90)? 0: 100;
            switch (s.game_condition)
            {
                case GameCondition::FAR_FROM_ALL:
                    if(!boost_used && s.next_checkpoint_angle < 10)
                    {
                        return std::string("BOOST"); 
                    }
                    break;
                case GameCondition::CLOSE_TO_CHECKPOINT_ONLY:
                    // if (!(s.next_checkpoint_angle > 90 || s.next_checkpoint_angle < -90))
                    // {
                    //     thrust = 50;
                    // }
                    break;
                case GameCondition::CLOSE_TO_OPPONENT_ONLY:
                    break;
                case GameCondition::CLOSE_TO_ALL:
                    if(!boost_used && s.next_checkpoint_angle < 10)
                    {
                        return std::string("BOOST"); 
                    }
                    return std::to_string(thrust);
            }
            
            return std::to_string(thrust); 
        };

    // game loop

    GameState s{};
    while (1) {
        cin >> s.x >> s.y >> s.next_checkpoint_x >> s.next_checkpoint_y >> s.next_checkpoint_dist >> s.next_checkpoint_angle; cin.ignore();
        cin >> s.opponent_x >> s.opponent_y; cin.ignore();

        int dist_x = s.next_checkpoint_x - s.opponent_x;
        int dist_y = s.next_checkpoint_y - s.opponent_y;
        s.opponent_checkpoint_dist = round(sqrt(dist_x*dist_x + dist_y*dist_y));

        dist_x = s.x - s.opponent_x;
        dist_y = s.y - s.opponent_y;
        s.opponent_dist = round(sqrt(dist_x*dist_x + dist_y*dist_y));

        s.game_condition = GameCondition::FAR_FROM_ALL;
        if (s.opponent_dist < force_field && s.next_checkpoint_dist < checkpoint_radius)
        {
            s.game_condition = GameCondition::CLOSE_TO_ALL;
        }
        else if(s.opponent_dist < force_field)
        {
            s.game_condition = GameCondition::CLOSE_TO_OPPONENT_ONLY;
        }
        else if(s.next_checkpoint_dist < checkpoint_radius)
        {
            s.game_condition = GameCondition::CLOSE_TO_CHECKPOINT_ONLY;
        }

        cerr << "opponent_checkpoint_dist: " << s.opponent_checkpoint_dist << endl;
        cerr << "opponent_dist: " << s.opponent_dist << endl;
        cerr << "next_checkpoint_dist: " << s.next_checkpoint_dist << endl;
        cerr << "next_checkpoint_angle: " << s.next_checkpoint_angle << endl;
        cerr << "game_condition: " << (int)s.game_condition << endl;


        // Write an action using cout. DON'T FORGET THE "<< endl"
        // To debug: cerr << "Debug messages..." << endl;
       
        // You have to output the target position
        // followed by the power (0 <= thrust <= 100)
        // i.e.: "x y thrust"
        cout << s.next_checkpoint_x << " " << s.next_checkpoint_y << " ";
        cout << get_thrust_input(s) << endl;

        
    }
}