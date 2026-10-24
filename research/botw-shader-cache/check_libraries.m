#import <Foundation/Foundation.h>
#import <Metal/Metal.h>
int main(int argc,char **argv) { @autoreleasepool {
 if(argc!=2)return 2;
 id<MTLDevice> dev=MTLCreateSystemDefaultDevice(); if(!dev)return 3;
 NSString *dir=@(argv[1]); unsigned count=0,failed=0;
 for(NSString *name in [[NSFileManager defaultManager] contentsOfDirectoryAtPath:dir error:nil]) {
  if(![name hasSuffix:@".metallib"])continue;
  @autoreleasepool { NSError *err=nil; id<MTLLibrary> lib=[dev newLibraryWithURL:[NSURL fileURLWithPath:[dir stringByAppendingPathComponent:name]] error:&err];
   if(!lib){ failed++; fprintf(stderr,"%s: %s\n",name.UTF8String,err.localizedDescription.UTF8String); } else count++;
  }
 }
 printf("loaded=%u failed=%u\n",count,failed); return failed?1:0;
}}
