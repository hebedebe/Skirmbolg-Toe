#version 330 core

uniform sampler2D tex;
uniform vec3 colour_correction;

in vec2 uvs;
out vec4 f_color;

void main() {
    vec2 sample_pos = vec2(uvs.x, uvs.y);
    vec4 tex_ = texture(tex, sample_pos);
    f_color = vec4(tex_.r * colour_correction.x, tex_.g * colour_correction.y, tex_.b * colour_correction.z, 1.0);
}