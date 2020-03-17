#include <string.h>
void setup();
void build();
void check();
void install();
int main(int argc,char* argv[]){
  if(strcmp(argv[1],"setup")==0){
    setup();
  }
  if(strcmp(argv[1],"build")==0){
    build();
  }
  if(strcmp(argv[1],"check")==0){
    check();
  }
  if(strcmp(argv[1],"install")==0){
    install();
  }
}
