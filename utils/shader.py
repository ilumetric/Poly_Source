# Shader Uniform
vs_uni = '''
    uniform mat4 view_mat;
    uniform float Z_Bias;
    

    vec4 pos_view;
    
    in vec3 pos;




    void main()
    {
        pos_view = view_mat * vec4(pos, 1.0f);
        pos_view.z = pos_view.z - Z_Bias / pos_view.z; 
        gl_Position = pos_view;
    }
'''

fs_uni = '''
    uniform vec4 color;
    out vec4 fragColor;

    void main()
    {
        fragColor = vec4(color.xyz, color.w);
    }

'''
 


# Shader Smooth
vs_sm = '''
    uniform mat4 view_mat;
    uniform float Z_Bias;
    

    vec4 pos_view;
    
    in vec3 pos;
    in vec4 col;

    out vec4 color;

    void main()
    {
        pos_view = view_mat * vec4(pos, 1.0f);
        color = col;
        pos_view.z = pos_view.z - Z_Bias / pos_view.z; 
        gl_Position = pos_view;
    }
'''

fs_sm = '''
    in vec4 color;
    out vec4 fragColor;

    void main()
    {
        fragColor  = vec4(color.xyz, color.w);
    }
'''

