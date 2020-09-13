/*		-==========================-
		|		MLlib Example	   |
		-==========================-

How to draw a tile of a sprite.

Functions explained :
- void ML_InitTile(sprite, widthOfOneTile, heightOfOneTile);
- void ML_DrawTile(sprite, X, Y, whichTile);

When you want to use the tile system on a sprite, you need to
initialize the sprite with ML_InitTile.
Then you can use ML_DrawTile ! :-)

Author : Minishlink
MLlib Website : http://louislagrange.free.fr/MLlib

Thanks ! 													*/

#include <MLlib.h>
#include "rick8_gimp_png.h"
#include "ricks_mp3.h"
#include "FreeSerif_ttf.h"

#define ANIM_TICK 5

#define FREE_SERIF 0
#define HAPPY_HELL 1

void refreshButtonPressedText(u32 pressed, char *text)
{
	if (pressed & WPAD_BUTTON_A)
	{
		strcpy(text, "Pressed A");
	}
	if (pressed & WPAD_BUTTON_B)
	{
		strcpy(text, "Pressed B");
	}
	if (pressed & WPAD_BUTTON_UP)
	{
		strcpy(text, "Pressed UP");
	}
	if (pressed & WPAD_BUTTON_DOWN)
	{
		strcpy(text, "Pressed DOWN");
	}
	if (pressed & WPAD_BUTTON_LEFT)
	{
		strcpy(text, "Pressed LEFT");
	}
	if (pressed & WPAD_BUTTON_RIGHT)
	{
		strcpy(text, "Pressed RIGHT");
	}
	if (pressed & WPAD_BUTTON_PLUS)
	{
		strcpy(text, "Pressed PLUS");
	}
	if (pressed & WPAD_BUTTON_MINUS)
	{
		strcpy(text, "Pressed MINUS");
	}
	if (pressed & WPAD_BUTTON_1)
	{
		strcpy(text, "Pressed 1");
	}
	if (pressed & WPAD_BUTTON_2)
	{
		strcpy(text, "Pressed 2");
	}
}

int main(int argc, char **argv)
{
	// Initialize the engine
	ML_Init();
	ML_EnableTextureAntiAliasing(); // it's better with TTF fonts if they are moving
	srand(time(NULL));

	// Position of the welcome text (moveable)
	int welcomeTextX = 20, welcomeTextY = 15;

	// Position of the "Button pressed" text
	int pressingX = 15;
	int pressingY = 100;

	// The font to use
	int TTF = FREE_SERIF;

	// Load the font and set the styles and size
	ML_Font font;
	ML_LoadFontFromBuffer(&font, FreeSerif_ttf, FreeSerif_ttf_size, 24);
	font.style = FONT_DEFAULT | FONT_UNDERLINE;

	// Result flag buffer
	char flag[37];

	// Strings to combine the flag from
	char w1[] = "Welcome";
	char w2[] = "to";
	char w3[] = "our";
	char w4[] = "Great";
	char w5[] = "Flag";
	char w6[] = "{Service_Revolution}!";

	// Strings for the two texts lastButtons and actual flag string
	char lastPressedChar[50] = "No buttons pressed yet ...";
	char flagString[50] = "No flag yet ...";
	char textCombined[100];

	// actual char pointer to print
	char *lastPressedCharReal = &lastPressedChar;
	char *flagStringReal = &flagString;

	// correct key input counter. If counter == 9, we win
	int counter = 0;

	// Last button state cached
	u32 lastButtonState = 0x00;

	// Sprite Stuff
	ML_Image spriteData;
	ML_Sprite sprite;
	if (ML_LoadSpriteFromBuffer(&spriteData, &sprite, rick8_gimp_png, 300, 200) == 0)
	{
		return 0;
	}
	// Set tile size to 76 x 62 (one rickroll picture)
	ML_InitTile(&sprite, 76, 62);
	ML_SetSpriteScale(&sprite, 4, 4);

	// Set current frame of the sprite to 0
	sprite.currentFrame = 0;

	// Animation counter. Increases each ANIM_TICK
	int animCounter = 0;

	//Init MOD MODPlay
	ML_InitMP3();

	while (1)
	{
		if (!ML_IsPlayingMP3()) {
			ML_PlayMP3FromBuffer(ricks_mp3, ricks_mp3_size);
		}

		if (Wiimote[0].Newpress.Home)
		{
			ML_StopMP3();
			ML_DeleteImage(&spriteData);
			ML_Exit();
		}

		// Scan for new inputs
		WPAD_ScanPads();

		// Move the text, just for the lulz
		if (Wiimote[0].Held.Right)
			welcomeTextX++;
		else if (Wiimote[0].Held.Left)
			welcomeTextX--;
		if (Wiimote[0].Held.Down)
			welcomeTextY++;
		else if (Wiimote[0].Held.Up)
			welcomeTextY--;

		// Build the combined welcome message from the string parts
		sprintf(textCombined, "%s %s %s %s %s%s", w1, w2, w3, w4, w5, w6);

		// Draw the welcome text
		ML_DrawText(&font, welcomeTextX, welcomeTextY, textCombined);

		// Get pressed buttons and
		u32 pressed = WPAD_ButtonsDown(0);

		// Check, if the last button state has changed in the last frame and any button is pressed at all
		if (pressed > 0)
		{

			refreshButtonPressedText(pressed, lastPressedCharReal);

			if (counter == 9 && (pressed & WPAD_BUTTON_UP))
			{
				flag[18] = w1[6];
				flag[16] = w6[12];

				flagStringReal = &flag;
			}

			if (counter == 8 && (pressed & WPAD_BUTTON_UP))
			{
				flag[13] = w4[2];
				flag[8] = w6[16];

				counter += 1;
			}
			else
			{
				if (counter == 8 && pressed && !(pressed & WPAD_BUTTON_UP))
				{
					counter = 0;
				}
			}

			if (counter == 7 && (pressed & WPAD_BUTTON_DOWN))
			{
				flag[27] = w4[3];
				flag[14] = w6[8];
				flag[30] = w5[0]+0x20;
				flag[19] = w6[18];

				counter += 1;
			}
			else
			{
				if (counter == 7 && pressed && !(pressed & WPAD_BUTTON_DOWN))
				{
					counter = 0;
				}
			}

			if (counter == 6 && (pressed & WPAD_BUTTON_DOWN))
			{
				flag[35] = w6[19];
		    flag[1] = w5[1] - 0x20;
		    flag[4] = w6[1];
		    flag[11] = w2[1];

				counter += 1;
			}
			else
			{
				if (counter == 6 && pressed && !(pressed & WPAD_BUTTON_DOWN))
				{
					counter = 0;
				}
			}

			if (counter == 5 && (pressed & WPAD_BUTTON_LEFT))
			{
				flag[3] = w6[7]-0x20;
		    flag[33] = w5[3];
		    flag[15] = w4[4];
		    flag[36] = 0;

				counter += 1;
			}
			else
			{
				if (counter == 5 && pressed && !(pressed & WPAD_BUTTON_LEFT))
				{
					counter = 0;
				}
			}

			if (counter == 4 && (pressed & WPAD_BUTTON_RIGHT))
			{
				flag[10] = w5[1];
		    flag[24] = w4[0]+0x20;
		    flag[21] = w1[1];
		    flag[9] = w6[8];

				counter += 1;
			}
			else
			{
				if (counter == 4 && pressed && !(pressed & WPAD_BUTTON_RIGHT))
				{
					counter = 0;
				}
			}

			if (counter == 3 && (pressed & WPAD_BUTTON_LEFT))
			{
				flag[22] = w4[1];
		    flag[17] = w6[8];
		    flag[23] = w6[8];
		    flag[5] = w6[0];

				counter += 1;
			}
			else
			{
				if (counter == 3 && pressed && !(pressed & WPAD_BUTTON_LEFT))
				{
					counter = 0;
				}
			}

			if (counter == 2 && (pressed & WPAD_BUTTON_RIGHT))
			{
				flag[12] = w6[11];
		    flag[26] = w6[7];
		    flag[7] = w6[5];
		    flag[25] = w6[9]+0x20;

				counter += 1;
			}
			else
			{
				if (counter == 2 && pressed && !(pressed & WPAD_BUTTON_RIGHT))
				{
					counter = 0;
				}
			}

			if (counter == 1 && (pressed & WPAD_BUTTON_B))
			{
				flag[2] = w6[13]-0x20;
		    flag[28] = w2[0];
		    flag[20] = w6[15];
		    flag[6] = w1[0];

				counter += 1;
			}
			else
			{
				if (counter == 1 && pressed && !(pressed & WPAD_BUTTON_B))
				{
					counter = 0;
				}
			}

			if (counter == 0 && (pressed & WPAD_BUTTON_A))
			{

				    flag[34] = w6[1]+0x20;
				    flag[31] = w1[2];
				    flag[29] = w6[8];
				    flag[32] = w4[3];
						flag[0] = w4[3] - 0x20;

				counter += 1;
			}
		}

		// Increase animation counter
		animCounter++;
		if (animCounter % ANIM_TICK == 0)
		{
			// Increase frame and wrap around
			sprite.currentFrame++;
			if (sprite.currentFrame == 27)
			{
				sprite.currentFrame = 0;
			}
		}

		// Draw current rickroll gif
		ML_DrawTile(&sprite, sprite.x, sprite.y, sprite.currentFrame);
		ML_DrawText(&font, pressingX, pressingY, lastPressedCharReal);
		ML_DrawText(&font, pressingX, pressingY + 30, flagStringReal);

		ML_Refresh();
	}

	return 0;
}
