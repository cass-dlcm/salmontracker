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


int shift_ReadAllFromFile(shift **head);
shift* shift_ListToArray(shift *head, int shift_count);

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
	int shift_count = shift_ReadAllFromFile(&head);
	
	shift *shift_arr;
	shift_arr = shift_ListToArray(head, shift_count);
	
	printf("\n\nWelcome to the Salmon Run Match Analyzer!\n");
	int input = -1;
	printf("Please select a subset of matches to work with.\n");
	printf("[0]: All Matches\n");
	printf("[1]: Select By Stage\n");
	printf("[2]: Select By Special\n");
	printf("[3]: Select By Weapon\n");
	printf("[4]: Select By Event\n");
	printf("[5]: Select By Tide\n");
	printf("[6]: Select By Hazard Level\n");
	printf("[9]: to quit\n");
	printf("Please select an option and press enter: ");
	scanf("%d", &input);
	
	switch (input) {
		case 0:
			break;
		case 1:
			printf("Pick from the following options:\n");
			string_list_PrintAll(stages);
			printf("[-1]: to go back\n");
			break;
		case 2:
			break;
		case 3:
			break;
		case 4:
			break;
		case 5:
			break;
		case 6:
			break;
		case 9:
			return;
			break;
	}
}


int shift_ReadAllFromFile(shift **head) {
	FILE *shifts = fopen("salmon.csv", "r");
	char c;
	int a = 0;
	do {
		fscanf(shifts, "%c", &c);
	} while (c != '\n');
	while (!feof(shifts)) {
		a++;
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
	return a;
}

shift* shift_ListToArray(shift *head, int shift_count) {
	shift *shift_arr = malloc(sizeof(shift)*shift_count);
	for (int i = 0; i < shift_count; i++) {
		shift_arr[i] = *head;
		head = head->next;
	}
	printf("Converted shift list to array!\n");
	return shift_arr;
}

// WIP
/*shift* shift_FindAllByWeapon(shift *array, int shift_count, short weapon_id) {
	shift *shift_lsit;
	for (int i = 0; i < shift_count; i++) {
		if ((array[i].players.[0].weapon[0] == weapon_id || array[i].players.[0].weapon[1] == weapon_id || array[i].players.[0].weapon[2] == weapon_id)
		 || (array[i].players.[1].weapon[0] == weapon_id || array[i].players.[1].weapon[1] == weapon_id || array[i].players.[1].weapon[2] == weapon_id)
		 || (array[i].players.[2].weapon[0] == weapon_id || array[i].players.[2].weapon[1] == weapon_id || array[i].players.[2].weapon[2] == weapon_id)
		 || (array[i].players.[3].weapon[0] == weapon_id || array[i].players.[3].weapon[1] == weapon_id || array[i].players.[3].weapon[2] == weapon_id)) {
			shift *new = malloc(sizeof(shift);
			new->statink_id = array[i].statink_id;
			new->rotation_period = array[i].rotation_period;
			new->shift_start = array[i].shift_start;
			new->splatnet_number = array[i].splatnet_number;
			new->stage = array[i].stage;
			new->clear_wave = array[i].clear_wave;
			
			new->fail_reason = string_list_FindIndexByString(fail_reasons, getfield(string_two, 10));
			
			new->hazard_level = round(10*atof(getfield(string_two, 11)));
			
			new->title_before_name = string_list_FindIndexByString(titles, getfield(string_two, 13));
			
			new->title_before_num = atoi(getfield(string_two, 14));
			
			new->title_after_name = string_list_FindIndexByString(titles, getfield(string_two, 16));
			
			new->title_after_num = atoi(getfield(string_two, 17));
			// get all general wave info
			for (int i = 0; i < 3; i++) {
				
				new->waves[i].event = string_list_FindIndexByString(events, getfield(string_two, 19 + 8 * i));
				
				new->waves[i].water = string_list_FindIndexByString(water_levels, getfield(string_two, 21 + 8 * i));
				
				new->waves[i].quota = atoi(getfield(string_two, 22 + 8 * i));
				
				new->waves[i].delivers = atoi(getfield(string_two, 23 + 8 * i));
				
				new->waves[i].appearances = atoi(getfield(string_two, 24 + 8 * i));
				
				new->waves[i].power_eggs = atoi(getfield(string_two, 25 + 8 * i));
			}
			
			for (int i = 0; i < 4; i++) {
				
				strcpy(new->players[i].id, getfield(string_two, 42 + 17 * i));
				
				strcpy(new->players[i].name, getfield(string_two, 43 + 17 * i));
				
				for (int j = 0; j < 3; j++) {
					
					new->players[i].weapon[j] = string_list_FindIndexByString(weapons, getfield(string_two, 45 + 2 * j + 17 * i));
				}
				
				
				new->players[i].special = string_list_FindIndexByString(specials, getfield(string_two, 51 + 17 * i));
				
				for (int j = 0; j < 3; j++) {
					
					new->players[i].special_use[j] = atoi(getfield(string_two, 52 + j + 17 * i));
				}
				
				
				new->players[i].player_rescues = atoi(getfield(string_two, 53 + 17 * i));
				
				new->players[i].players_rescued = atoi(getfield(string_two, 54 + 17 * i));
				
				new->players[i].golden_eggs = atoi(getfield(string_two, 55 + 17 * i));
				
				new->players[i].power_eggs = atoi(getfield(string_two, 56 + 17 * i));
			}
			
			for (int i = 0; i < 9; i++) {
				
				new->boss_appearances[i] = atoi(getfield(string_two, 110 + i * 5));
			}
		}
	}
	
}*/

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
