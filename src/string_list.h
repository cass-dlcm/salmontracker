
typedef struct string_list {
	char string[30];
	struct string_list *next;
	struct string_list *prev;
} string_list;

void string_list_ReadFromFile(string_list **head, char *file_name);
void string_list_PrintAll(string_list *head);
int string_list_FindIndexByString(string_list *head, char *string);
const char *string_list_FindStringByIndex(string_list *head, int index);

void string_list_ReadFromFile(string_list **head, char *file_name) {
	FILE *file = fopen(file_name, "r");
	while (!feof(file)) {
		string_list *new = malloc(sizeof(string_list));
		fgets(new->string, 30, file);
		new->next == NULL;
		new->prev == NULL;
		if (!(*head)) {
			*head = new;
		} else {
			string_list *temp = *head;
			while (temp->next) {
				temp = temp->next;
			}
			temp->next = new;
			new->prev = temp;
		}
	}
}

void string_list_PrintAll(string_list *head) {
	while (head) {
		printf("%s", head->string);
		head = head->next;
	}
}

int string_list_FindIndexByString(string_list *head, char *string) {
	int index = 0;
	while (head) {
		if (strncmp(head->string, string, strlen(string) - 1) == 0) {
			return index;
		}
		head = head->next;
		index++;
	}
	return -1;
}

const char *string_list_FindStringByIndex(string_list *head, int index) {
	if (index == -1) {
		return "\n";
	}
	for (int i = 0; i < index; i++) {
		head = head->next;
	}
	return head->string;
}
