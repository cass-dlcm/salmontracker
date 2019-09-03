#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include "string_list.h"


typedef struct wave {
	short event;
	short water;
	short quota;
	short delivers;
	short appearances;
	int power_eggs;
} wave;

typedef struct player {
	char id[30];
	char name[11];
	short weapon[3];
	short special;
	short special_use[3];
	short player_rescues;
	short players_rescued;
	short golden_eggs;
	int power_eggs;
	short boss_kills[9];
} player;

typedef struct shift {
	int statink_id;
	int rotation_period;
	long shift_start;
	int splatnet_number;
	short stage;
	short clear_wave;
	short fail_reason;
	int hazard_level;
	short title_before_name;
	int title_before_num;
	short title_after_name;
	int title_after_num;
	wave waves[3];
	player players[4];
	short boss_appearances[9];
	struct shift *next;
	struct shift *prev;
} shift;

string_list *stages = NULL;
string_list *fail_reasons = NULL;
string_list *titles = NULL;
string_list *events = NULL;
string_list *water_levels = NULL;
string_list *specials = NULL;
string_list *bosses = NULL;
string_list *weapons = NULL;


void shift_ReadAllFromFile(shift **head);

const char* getfield(char* line, int num);

int main (int argc, char *argv) {
	string_list_ReadFromFile(&stages, "stages.txt");
	printf("Loaded all Stages!\n");
	
	string_list_ReadFromFile(&fail_reasons, "fail_reasons.txt");
	printf("Loaded all Fail Reasons!\n");
	
	string_list_ReadFromFile(&titles, "titles.txt");
	printf("Loaded all Titles!\n");
	
	string_list_ReadFromFile(&events, "events.txt");
	printf("Loaded all Events!\n");
	
	string_list_ReadFromFile(&water_levels, "water_levels.txt");
	printf("Loaded all Water Levels!\n");
	
	string_list_ReadFromFile(&specials, "specials.txt");
	printf("Loaded all Specials!\n");
	
	string_list_ReadFromFile(&bosses, "bosses.txt");
	printf("Loaded all Bosses!\n");
	
	string_list_ReadFromFile(&weapons, "weapons.txt");
	printf("Loaded all Weapons!\n");
	
	shift *head = NULL;
	shift_ReadAllFromFile(&head);
}



void shift_ReadAllFromFile(shift **head) {
	FILE *shifts = fopen("salmon.csv", "r");
	char c;
	do {
		fscanf(shifts, "%c", &c);
	} while (c != '\n');
	while (!feof(shifts)) {
		shift *new = malloc(sizeof(shift));
		char string[10000];
		fgets(string, 10000, shifts);
		char string_two[10000];
		strcpy(string_two, string);
		new->statink_id = atoi(getfield(string_two, 1));
		strcpy(string_two, string);
		new->rotation_period = atoi(getfield(string_two, 2));
		strcpy(string_two, string);
		new->shift_start = atol(getfield(string_two, 3));
		strcpy(string_two, string);
		new->splatnet_number = atoi(getfield(string_two, 5));
		strcpy(string_two, string);
		new->stage = string_list_FindIndexByString(stages, getfield(string_two, 7));
		strcpy(string_two, string);
		new->clear_wave = atoi(getfield(string_two, 8));
		strcpy(string_two, string);
		new->fail_reason = string_list_FindIndexByString(fail_reasons, getfield(string_two, 10));
		strcpy(string_two, string);
		new->hazard_level = round(10*atof(getfield(string_two, 11)));
		strcpy(string_two, string);
		new->title_before_name = string_list_FindIndexByString(titles, getfield(string_two, 13));
		strcpy(string_two, string);
		new->title_before_num = atoi(getfield(string_two, 14));
		strcpy(string_two, string);
		new->title_after_name = string_list_FindIndexByString(titles, getfield(string_two, 16));
		strcpy(string_two, string);
		new->title_after_num = atoi(getfield(string_two, 17));
		// get all general wave info
		for (int i = 0; i < 3; i++) {
			strcpy(string_two, string);
			new->waves[i].event = string_list_FindIndexByString(events, getfield(string_two, 19 + 8 * i));
			strcpy(string_two, string);
			new->waves[i].water = string_list_FindIndexByString(water_levels, getfield(string_two, 21 + 8 * i));
			strcpy(string_two, string);
			new->waves[i].quota = atoi(getfield(string_two, 22 + 8 * i));
			strcpy(string_two, string);
			new->waves[i].delivers = atoi(getfield(string_two, 23 + 8 * i));
			strcpy(string_two, string);
			new->waves[i].appearances = atoi(getfield(string_two, 24 + 8 * i));
			strcpy(string_two, string);
			new->waves[i].power_eggs = atoi(getfield(string_two, 25 + 8 * i));
		}
		
		for (int i = 0; i < 4; i++) {
			strcpy(string_two, string);
			strcpy(new->players[i].id, getfield(string_two, 42 + 17 * i));
			strcpy(string_two, string);
			strcpy(new->players[i].name, getfield(string_two, 43 + 17 * i));
			
			for (int j = 0; j < 3; j++) {
				strcpy(string_two, string);
				new->players[i].weapon[j] = string_list_FindIndexByString(weapons, getfield(string_two, 45 + 2 * j + 17 * i));
			}
			
			strcpy(string_two, string);
			new->players[i].special = string_list_FindIndexByString(specials, getfield(string_two, 51 + 17 * i));
			
			for (int j = 0; j < 3; j++) {
				strcpy(string_two, string);
				new->players[i].special_use[j] = atoi(getfield(string_two, 52 + j + 17 * i));
			}
			
			strcpy(string_two, string);
			new->players[i].player_rescues = atoi(getfield(string_two, 53 + 17 * i));
			strcpy(string_two, string);
			new->players[i].players_rescued = atoi(getfield(string_two, 54 + 17 * i));
			strcpy(string_two, string);
			new->players[i].golden_eggs = atoi(getfield(string_two, 55 + 17 * i));
			strcpy(string_two, string);
			new->players[i].power_eggs = atoi(getfield(string_two, 56 + 17 * i));
		}
		
		for (int i = 0; i < 9; i++) {
			strcpy(string_two, string);
			new->boss_appearances[i] = atoi(getfield(string_two, 110 + i * 5));
		}
		
		new->next == NULL;
		new->prev == NULL;
		if (!(*head)) {
			*head = new;
		} else {
			shift *temp = *head;
			while (temp->next) {
				temp = temp->next;
			}
			temp->next = new;
			new->prev = temp;
		}
	}
	printf("Loaded all Shifts!\n");
}


const char* getfield(char* line, int num)
{
    const char* tok;
    for (tok = strtok(line, ",");
            tok && *tok;
            tok = strtok(NULL, ",\n"))
    {
        if (!--num)
            return tok;
    }
    return "";
}
