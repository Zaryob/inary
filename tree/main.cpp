#include <algorithm>
#include <iostream>
#include <string>
#include <vector>

#include "tree.hh"

using namespace std;

class Package
{
	public:
		Package( string name ) { this->name = name; };
		~Package() {};
		string getName() { return this->name; };
	private:
		string name;
};

typedef tree<Package> Tree;

int main(int argc, char *argv[])
{
	vector<string> dependencies;
	
	Package *kdebase = new Package("kdebase");
	Package *kdelibs = new Package("kdelibs");
	Package *kdeartwork = new Package("kdeartwork");
	Package *kdepim = new Package("kdepim");
	Package *glibc = new Package("glibc");
	Package *gcc = new Package("gcc");
	Package *xorg = new Package("xorg-x11");

	Tree depTree;
	Tree::iterator top, element;

	top = depTree.begin();
	
	/*
	 *	kde_
	 *	    |_kdebase_
	 *	    |         |_kdelibs
	 *	    |         |_kdeartwork_
	 *	    |                      |
	 *	    |                      |_xorg-x11_
	 *	    |                                 |_glibc
	 *	    |                                 |_gcc
	 *	    |
	 *	    |_kdepim_
	 *	             |_xorg-x11_
	 *	                        |_glibc
	 *	                        |_gcc
	 */

	element = depTree.insert( top, *kdebase );
	depTree.append_child( element, *kdelibs );
	element = depTree.append_child( element, *kdeartwork );
	element = depTree.append_child( element, *xorg  );
	depTree.append_child( element, *glibc );
	depTree.append_child( element, *gcc );
	element = depTree.insert( top, *kdepim );
	element = depTree.append_child( element, *xorg  );
	depTree.append_child( element, *glibc );
	depTree.append_child( element, *gcc );
 
	cout << "...Tracked Dependencies..." << endl;
	
	Tree::post_order_iterator sib_post = depTree.begin_post();
	while( sib_post != depTree.end_post() )
	{
		vector<string>::iterator p = find( dependencies.begin(), dependencies.end(), sib_post->getName() );

		if( p == dependencies.end() )
			dependencies.push_back( sib_post->getName() );

		++sib_post;
	}

	for( int i = 0; i < dependencies.size(); i++ )
		cout << dependencies[i] << endl;
	
	return 0;
}
